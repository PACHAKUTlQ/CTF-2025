package org.springframework.boot.loader.zip;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.channels.ClosedByInterruptException;
import java.nio.channels.ClosedChannelException;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.function.Supplier;
import org.springframework.boot.loader.log.DebugLogger;

class FileDataBlock implements CloseableDataBlock {
   private static final DebugLogger debug = DebugLogger.get(FileDataBlock.class);
   static FileDataBlock.Tracker tracker;
   private final FileDataBlock.FileAccess fileAccess;
   private final long offset;
   private final long size;

   FileDataBlock(Path path) throws IOException {
      this.fileAccess = new FileDataBlock.FileAccess(path);
      this.offset = 0L;
      this.size = Files.size(path);
   }

   FileDataBlock(FileDataBlock.FileAccess fileAccess, long offset, long size) {
      this.fileAccess = fileAccess;
      this.offset = offset;
      this.size = size;
   }

   public long size() throws IOException {
      return this.size;
   }

   public int read(ByteBuffer dst, long pos) throws IOException {
      if (pos < 0L) {
         throw new IllegalArgumentException("Position must not be negative");
      } else {
         this.ensureOpen(ClosedChannelException::new);
         long remaining = this.size - pos;
         if (remaining <= 0L) {
            return -1;
         } else {
            int originalDestinationLimit = -1;
            if ((long)dst.remaining() > remaining) {
               originalDestinationLimit = dst.limit();
               long updatedLimit = (long)dst.position() + remaining;
               dst.limit(updatedLimit > 2147483647L ? Integer.MAX_VALUE : (int)updatedLimit);
            }

            int result = this.fileAccess.read(dst, this.offset + pos);
            if (originalDestinationLimit != -1) {
               dst.limit(originalDestinationLimit);
            }

            return result;
         }
      }
   }

   void open() throws IOException {
      this.fileAccess.open();
   }

   public void close() throws IOException {
      this.fileAccess.close();
   }

   <E extends Exception> void ensureOpen(Supplier<E> exceptionSupplier) throws E {
      this.fileAccess.ensureOpen(exceptionSupplier);
   }

   FileDataBlock slice(long offset) throws IOException {
      return this.slice(offset, this.size - offset);
   }

   FileDataBlock slice(long offset, long size) {
      if (offset == 0L && size == this.size) {
         return this;
      } else if (offset < 0L) {
         throw new IllegalArgumentException("Offset must not be negative");
      } else if (size >= 0L && offset + size <= this.size) {
         debug.log("Slicing %s at %s with size %s", this.fileAccess, offset, size);
         return new FileDataBlock(this.fileAccess, this.offset + offset, size);
      } else {
         throw new IllegalArgumentException("Size must not be negative and must be within bounds");
      }
   }

   static {
      tracker = FileDataBlock.Tracker.NONE;
   }

   static class FileAccess {
      static final int BUFFER_SIZE = 10240;
      private final Path path;
      private int referenceCount;
      private FileChannel fileChannel;
      private boolean fileChannelInterrupted;
      private RandomAccessFile randomAccessFile;
      private ByteBuffer buffer;
      private long bufferPosition = -1L;
      private int bufferSize;
      private final Object lock = new Object();

      FileAccess(Path path) {
         if (!Files.isRegularFile(path, new LinkOption[0])) {
            throw new IllegalArgumentException(String.valueOf(path) + " must be a regular file");
         } else {
            this.path = path;
         }
      }

      int read(ByteBuffer dst, long position) throws IOException {
         synchronized(this.lock) {
            if (position < this.bufferPosition || position >= this.bufferPosition + (long)this.bufferSize) {
               this.fillBuffer(position);
            }

            if (this.bufferSize <= 0) {
               return this.bufferSize;
            } else {
               int offset = (int)(position - this.bufferPosition);
               int length = Math.min(this.bufferSize - offset, dst.remaining());
               dst.put(dst.position(), this.buffer, offset, length);
               dst.position(dst.position() + length);
               return length;
            }
         }
      }

      private void fillBuffer(long position) throws IOException {
         if (Thread.currentThread().isInterrupted()) {
            this.fillBufferUsingRandomAccessFile(position);
         } else {
            try {
               if (this.fileChannelInterrupted) {
                  this.repairFileChannel();
                  this.fileChannelInterrupted = false;
               }

               this.buffer.clear();
               this.bufferSize = this.fileChannel.read(this.buffer, position);
               this.bufferPosition = position;
            } catch (ClosedByInterruptException var4) {
               this.fileChannelInterrupted = true;
               this.fillBufferUsingRandomAccessFile(position);
            }

         }
      }

      private void fillBufferUsingRandomAccessFile(long position) throws IOException {
         if (this.randomAccessFile == null) {
            this.randomAccessFile = new RandomAccessFile(this.path.toFile(), "r");
            FileDataBlock.tracker.openedFileChannel(this.path);
         }

         byte[] bytes = new byte[10240];
         this.randomAccessFile.seek(position);
         int len = this.randomAccessFile.read(bytes);
         this.buffer.clear();
         if (len > 0) {
            this.buffer.put(bytes, 0, len);
         }

         this.bufferSize = len;
         this.bufferPosition = position;
      }

      private void repairFileChannel() throws IOException {
         FileDataBlock.tracker.closedFileChannel(this.path);
         this.fileChannel = FileChannel.open(this.path, StandardOpenOption.READ);
         FileDataBlock.tracker.openedFileChannel(this.path);
      }

      void open() throws IOException {
         synchronized(this.lock) {
            if (this.referenceCount == 0) {
               FileDataBlock.debug.log("Opening '%s'", this.path);
               this.fileChannel = FileChannel.open(this.path, StandardOpenOption.READ);
               this.buffer = ByteBuffer.allocateDirect(10240);
               FileDataBlock.tracker.openedFileChannel(this.path);
            }

            ++this.referenceCount;
            FileDataBlock.debug.log("Reference count for '%s' incremented to %s", this.path, this.referenceCount);
         }
      }

      void close() throws IOException {
         synchronized(this.lock) {
            if (this.referenceCount != 0) {
               --this.referenceCount;
               if (this.referenceCount == 0) {
                  FileDataBlock.debug.log("Closing '%s'", this.path);
                  this.buffer = null;
                  this.bufferPosition = -1L;
                  this.bufferSize = 0;
                  this.fileChannel.close();
                  FileDataBlock.tracker.closedFileChannel(this.path);
                  this.fileChannel = null;
                  if (this.randomAccessFile != null) {
                     this.randomAccessFile.close();
                     FileDataBlock.tracker.closedFileChannel(this.path);
                     this.randomAccessFile = null;
                  }
               }

               FileDataBlock.debug.log("Reference count for '%s' decremented to %s", this.path, this.referenceCount);
            }
         }
      }

      <E extends Exception> void ensureOpen(Supplier<E> exceptionSupplier) throws E {
         synchronized(this.lock) {
            if (this.referenceCount == 0) {
               throw (Exception)exceptionSupplier.get();
            }
         }
      }

      public String toString() {
         return this.path.toString();
      }
   }

   interface Tracker {
      FileDataBlock.Tracker NONE = new FileDataBlock.Tracker() {
         public void openedFileChannel(Path path) {
         }

         public void closedFileChannel(Path path) {
         }
      };

      void openedFileChannel(Path path);

      void closedFileChannel(Path path);
   }
}
