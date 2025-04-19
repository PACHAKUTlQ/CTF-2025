package org.springframework.boot.loader.nio.file;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

final class UriPathEncoder {
   private static final char[] ALLOWED = "/:@-._~!$&'()*+,;=".toCharArray();

   private UriPathEncoder() {
   }

   static String encode(String path) {
      byte[] bytes = path.getBytes(StandardCharsets.UTF_8);
      byte[] var2 = bytes;
      int var3 = bytes.length;

      for(int var4 = 0; var4 < var3; ++var4) {
         byte b = var2[var4];
         if (!isAllowed(b)) {
            return encode(bytes);
         }
      }

      return path;
   }

   private static String encode(byte[] bytes) {
      ByteArrayOutputStream result = new ByteArrayOutputStream(bytes.length);
      byte[] var2 = bytes;
      int var3 = bytes.length;

      for(int var4 = 0; var4 < var3; ++var4) {
         byte b = var2[var4];
         if (isAllowed(b)) {
            result.write(b);
         } else {
            result.write(37);
            result.write(Character.toUpperCase(Character.forDigit(b >> 4 & 15, 16)));
            result.write(Character.toUpperCase(Character.forDigit(b & 15, 16)));
         }
      }

      return result.toString(StandardCharsets.UTF_8);
   }

   private static boolean isAllowed(int ch) {
      char[] var1 = ALLOWED;
      int var2 = var1.length;

      for(int var3 = 0; var3 < var2; ++var3) {
         char allowed = var1[var3];
         if (ch == allowed) {
            return true;
         }
      }

      return isAlpha(ch) || isDigit(ch);
   }

   private static boolean isAlpha(int ch) {
      return ch >= 97 && ch <= 122 || ch >= 65 && ch <= 90;
   }

   private static boolean isDigit(int ch) {
      return ch >= 48 && ch <= 57;
   }
}
