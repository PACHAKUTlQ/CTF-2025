package org.springframework.boot.loader.jar;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.security.CodeSigner;
import java.security.cert.Certificate;
import java.util.jar.JarEntry;
import org.springframework.boot.loader.zip.ZipContent;

final class SecurityInfo {
   static final SecurityInfo NONE = new SecurityInfo((Certificate[][])null, (CodeSigner[][])null);
   private final Certificate[][] certificateLookups;
   private final CodeSigner[][] codeSignerLookups;

   private SecurityInfo(Certificate[][] entryCertificates, CodeSigner[][] entryCodeSigners) {
      this.certificateLookups = entryCertificates;
      this.codeSignerLookups = entryCodeSigners;
   }

   Certificate[] getCertificates(ZipContent.Entry contentEntry) {
      return this.certificateLookups != null ? (Certificate[])this.clone(this.certificateLookups[contentEntry.getLookupIndex()]) : null;
   }

   CodeSigner[] getCodeSigners(ZipContent.Entry contentEntry) {
      return this.codeSignerLookups != null ? (CodeSigner[])this.clone(this.codeSignerLookups[contentEntry.getLookupIndex()]) : null;
   }

   private <T> T[] clone(T[] array) {
      return array != null ? (Object[])array.clone() : null;
   }

   static SecurityInfo get(ZipContent content) {
      if (!content.hasJarSignatureFile()) {
         return NONE;
      } else {
         try {
            return load(content);
         } catch (IOException var2) {
            throw new UncheckedIOException(var2);
         }
      }
   }

   private static SecurityInfo load(ZipContent content) throws IOException {
      int size = content.size();
      boolean hasSecurityInfo = false;
      Certificate[][] entryCertificates = new Certificate[size][];
      CodeSigner[][] entryCodeSigners = new CodeSigner[size][];
      JarEntriesStream entries = new JarEntriesStream(content.openRawZipData().asInputStream());

      try {
         for(JarEntry entry = entries.getNextEntry(); entry != null; entry = entries.getNextEntry()) {
            ZipContent.Entry relatedEntry = content.getEntry(entry.getName());
            if (relatedEntry != null && entries.matches(relatedEntry.isDirectory(), relatedEntry.getUncompressedSize(), relatedEntry.getCompressionMethod(), () -> {
               return relatedEntry.openContent().asInputStream();
            })) {
               Certificate[] certificates = entry.getCertificates();
               CodeSigner[] codeSigners = entry.getCodeSigners();
               if (certificates != null || codeSigners != null) {
                  hasSecurityInfo = true;
                  entryCertificates[relatedEntry.getLookupIndex()] = certificates;
                  entryCodeSigners[relatedEntry.getLookupIndex()] = codeSigners;
               }
            }
         }
      } catch (Throwable var11) {
         try {
            entries.close();
         } catch (Throwable var10) {
            var11.addSuppressed(var10);
         }

         throw var11;
      }

      entries.close();
      return !hasSecurityInfo ? NONE : new SecurityInfo(entryCertificates, entryCodeSigners);
   }
}
