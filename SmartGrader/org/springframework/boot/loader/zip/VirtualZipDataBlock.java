package org.springframework.boot.loader.zip;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;

class VirtualZipDataBlock extends VirtualDataBlock implements CloseableDataBlock {
   private final CloseableDataBlock data;

   VirtualZipDataBlock(CloseableDataBlock data, NameOffsetLookups nameOffsetLookups, ZipCentralDirectoryFileHeaderRecord[] centralRecords, long[] centralRecordPositions) throws IOException {
      this.data = data;
      List<DataBlock> parts = new ArrayList();
      List<DataBlock> centralParts = new ArrayList();
      long offset = 0L;
      long sizeOfCentralDirectory = 0L;

      for(int i = 0; i < centralRecords.length; ++i) {
         ZipCentralDirectoryFileHeaderRecord centralRecord = centralRecords[i];
         int nameOffset = nameOffsetLookups.get(i);
         long centralRecordPos = centralRecordPositions[i];
         DataBlock name = new VirtualZipDataBlock.DataPart(centralRecordPos + 46L + (long)nameOffset, Short.toUnsignedLong(centralRecord.fileNameLength()) - (long)nameOffset);
         long localRecordPos = Integer.toUnsignedLong(centralRecord.offsetToLocalHeader());
         ZipLocalFileHeaderRecord localRecord = ZipLocalFileHeaderRecord.load(this.data, localRecordPos);
         DataBlock content = new VirtualZipDataBlock.DataPart(localRecordPos + localRecord.size(), (long)centralRecord.compressedSize());
         boolean hasDescriptorRecord = ZipDataDescriptorRecord.isPresentBasedOnFlag(centralRecord);
         ZipDataDescriptorRecord dataDescriptorRecord = !hasDescriptorRecord ? null : ZipDataDescriptorRecord.load(data, localRecordPos + localRecord.size() + content.size());
         sizeOfCentralDirectory += this.addToCentral(centralParts, centralRecord, centralRecordPos, name, (int)offset);
         offset += this.addToLocal(parts, centralRecord, localRecord, dataDescriptorRecord, name, content);
      }

      parts.addAll(centralParts);
      ZipEndOfCentralDirectoryRecord eocd = new ZipEndOfCentralDirectoryRecord((short)centralRecords.length, (int)sizeOfCentralDirectory, (int)offset);
      parts.add(new ByteArrayDataBlock(eocd.asByteArray()));
      this.setParts(parts);
   }

   private long addToCentral(List<DataBlock> parts, ZipCentralDirectoryFileHeaderRecord originalRecord, long originalRecordPos, DataBlock name, int offsetToLocalHeader) throws IOException {
      ZipCentralDirectoryFileHeaderRecord record = originalRecord.withFileNameLength((short)((int)(name.size() & 65535L))).withOffsetToLocalHeader(offsetToLocalHeader);
      int originalExtraFieldLength = Short.toUnsignedInt(originalRecord.extraFieldLength());
      int originalFileCommentLength = Short.toUnsignedInt(originalRecord.fileCommentLength());
      int extraFieldAndCommentSize = originalExtraFieldLength + originalFileCommentLength;
      parts.add(new ByteArrayDataBlock(record.asByteArray()));
      parts.add(name);
      if (extraFieldAndCommentSize > 0) {
         parts.add(new VirtualZipDataBlock.DataPart(originalRecordPos + originalRecord.size() - (long)extraFieldAndCommentSize, (long)extraFieldAndCommentSize));
      }

      return record.size();
   }

   private long addToLocal(List<DataBlock> parts, ZipCentralDirectoryFileHeaderRecord centralRecord, ZipLocalFileHeaderRecord originalRecord, ZipDataDescriptorRecord dataDescriptorRecord, DataBlock name, DataBlock content) throws IOException {
      ZipLocalFileHeaderRecord record = originalRecord.withFileNameLength((short)((int)(name.size() & 65535L)));
      long originalRecordPos = Integer.toUnsignedLong(centralRecord.offsetToLocalHeader());
      int extraFieldLength = Short.toUnsignedInt(originalRecord.extraFieldLength());
      parts.add(new ByteArrayDataBlock(record.asByteArray()));
      parts.add(name);
      if (extraFieldLength > 0) {
         parts.add(new VirtualZipDataBlock.DataPart(originalRecordPos + originalRecord.size() - (long)extraFieldLength, (long)extraFieldLength));
      }

      parts.add(content);
      if (dataDescriptorRecord != null) {
         parts.add(new ByteArrayDataBlock(dataDescriptorRecord.asByteArray()));
      }

      return record.size() + content.size() + (dataDescriptorRecord != null ? dataDescriptorRecord.size() : 0L);
   }

   public void close() throws IOException {
      this.data.close();
   }

   final class DataPart implements DataBlock {
      private final long offset;
      private final long size;

      DataPart(long offset, long size) {
         this.offset = offset;
         this.size = size;
      }

      public long size() throws IOException {
         return this.size;
      }

      public int read(ByteBuffer dst, long pos) throws IOException {
         int remaining = (int)(this.size - pos);
         if (remaining <= 0) {
            return -1;
         } else {
            int originalLimit = -1;
            if (dst.remaining() > remaining) {
               originalLimit = dst.limit();
               dst.limit(dst.position() + remaining);
            }

            int result = VirtualZipDataBlock.this.data.read(dst, this.offset + pos);
            if (originalLimit != -1) {
               dst.limit(originalLimit);
            }

            return result;
         }
      }
   }
}
