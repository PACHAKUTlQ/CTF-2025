package org.springframework.boot.loader.zip;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Collection;
import java.util.Iterator;

class VirtualDataBlock implements DataBlock {
   private DataBlock[] parts;
   private long[] offsets;
   private long size;
   private volatile int lastReadPart = 0;

   protected VirtualDataBlock() {
   }

   VirtualDataBlock(Collection<? extends DataBlock> parts) throws IOException {
      this.setParts(parts);
   }

   protected void setParts(Collection<? extends DataBlock> parts) throws IOException {
      this.parts = (DataBlock[])parts.toArray((x$0) -> {
         return new DataBlock[x$0];
      });
      this.offsets = new long[parts.size()];
      long size = 0L;
      int i = 0;

      DataBlock part;
      for(Iterator var5 = parts.iterator(); var5.hasNext(); size += part.size()) {
         part = (DataBlock)var5.next();
         this.offsets[i++] = size;
      }

      this.size = size;
   }

   public long size() throws IOException {
      return this.size;
   }

   public int read(ByteBuffer dst, long pos) throws IOException {
      if (pos >= 0L && pos < this.size) {
         int lastReadPart = this.lastReadPart;
         int partIndex = 0;
         long offset = 0L;
         int result = 0;
         if (pos >= this.offsets[lastReadPart]) {
            partIndex = lastReadPart;
            offset = this.offsets[lastReadPart];
         }

         while(partIndex < this.parts.length) {
            DataBlock part;
            int count;
            for(part = this.parts[partIndex]; pos >= offset && pos < offset + part.size(); pos += (long)count) {
               count = part.read(dst, pos - offset);
               result += Math.max(count, 0);
               if (count <= 0 || !dst.hasRemaining()) {
                  this.lastReadPart = partIndex;
                  return result;
               }
            }

            offset += part.size();
            ++partIndex;
         }

         return result;
      } else {
         return -1;
      }
   }
}
