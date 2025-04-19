package org.springframework.boot.loader.net.protocol.jar;

import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLStreamHandler;

public class Handler extends URLStreamHandler {
   private static final String PROTOCOL = "jar";
   private static final String SEPARATOR = "!/";
   static final Handler INSTANCE = new Handler();

   protected URLConnection openConnection(URL url) throws IOException {
      return JarUrlConnection.open(url);
   }

   protected void parseURL(URL url, String spec, int start, int limit) {
      if (spec.regionMatches(true, start, "jar:", 0, 4)) {
         throw new IllegalStateException("Nested JAR URLs are not supported");
      } else {
         int anchorIndex = spec.indexOf(35, limit);
         String path = this.extractPath(url, spec, start, limit, anchorIndex);
         String ref = anchorIndex != -1 ? spec.substring(anchorIndex + 1) : null;
         this.setURL(url, "jar", "", -1, (String)null, (String)null, path, (String)null, ref);
      }
   }

   private String extractPath(URL url, String spec, int start, int limit, int anchorIndex) {
      if (anchorIndex == start) {
         return this.extractAnchorOnlyPath(url);
      } else {
         return spec.length() >= 4 && spec.regionMatches(true, 0, "jar:", 0, 4) ? this.extractAbsolutePath(spec, start, limit) : this.extractRelativePath(url, spec, start, limit);
      }
   }

   private String extractAnchorOnlyPath(URL url) {
      return url.getPath();
   }

   private String extractAbsolutePath(String spec, int start, int limit) {
      int indexOfSeparator = indexOfSeparator(spec, start, limit);
      if (indexOfSeparator == -1) {
         throw new IllegalStateException("no !/ in spec");
      } else {
         String innerUrl = spec.substring(start, indexOfSeparator);
         this.assertInnerUrlIsNotMalformed(spec, innerUrl);
         return spec.substring(start, limit);
      }
   }

   private String extractRelativePath(URL url, String spec, int start, int limit) {
      String contextPath = this.extractContextPath(url, spec, start);
      String path = contextPath + spec.substring(start, limit);
      return Canonicalizer.canonicalizeAfter(path, indexOfSeparator(path) + 1);
   }

   private String extractContextPath(URL url, String spec, int start) {
      String contextPath = url.getPath();
      int lastSlash;
      if (spec.regionMatches(false, start, "/", 0, 1)) {
         lastSlash = indexOfSeparator(contextPath);
         if (lastSlash == -1) {
            throw new IllegalStateException("malformed context url:%s: no !/".formatted(new Object[]{url}));
         } else {
            return contextPath.substring(0, lastSlash + 1);
         }
      } else {
         lastSlash = contextPath.lastIndexOf(47);
         if (lastSlash == -1) {
            throw new IllegalStateException("malformed context url:%s".formatted(new Object[]{url}));
         } else {
            return contextPath.substring(0, lastSlash + 1);
         }
      }
   }

   private void assertInnerUrlIsNotMalformed(String spec, String innerUrl) {
      if (innerUrl.startsWith("nested:")) {
         org.springframework.boot.loader.net.protocol.nested.Handler.assertUrlIsNotMalformed(innerUrl);
      } else {
         try {
            new URL(innerUrl);
         } catch (MalformedURLException var4) {
            throw new IllegalStateException("invalid url: %s (%s)".formatted(new Object[]{spec, var4}));
         }
      }
   }

   protected int hashCode(URL url) {
      String protocol = url.getProtocol();
      int hash = protocol != null ? protocol.hashCode() : 0;
      String file = url.getFile();
      int indexOfSeparator = file.indexOf("!/");
      if (indexOfSeparator == -1) {
         return hash + file.hashCode();
      } else {
         String fileWithoutEntry = file.substring(0, indexOfSeparator);

         try {
            hash += (new URL(fileWithoutEntry)).hashCode();
         } catch (MalformedURLException var8) {
            hash += fileWithoutEntry.hashCode();
         }

         String entry = file.substring(indexOfSeparator + 2);
         return hash + entry.hashCode();
      }
   }

   protected boolean sameFile(URL url1, URL url2) {
      if (url1.getProtocol().equals("jar") && url2.getProtocol().equals("jar")) {
         String file1 = url1.getFile();
         String file2 = url2.getFile();
         int indexOfSeparator1 = file1.indexOf("!/");
         int indexOfSeparator2 = file2.indexOf("!/");
         if (indexOfSeparator1 != -1 && indexOfSeparator2 != -1) {
            String entry1 = file1.substring(indexOfSeparator1 + 2);
            String entry2 = file2.substring(indexOfSeparator2 + 2);
            if (!entry1.equals(entry2)) {
               return false;
            } else {
               try {
                  URL innerUrl1 = new URL(file1.substring(0, indexOfSeparator1));
                  URL innerUrl2 = new URL(file2.substring(0, indexOfSeparator2));
                  return super.sameFile(innerUrl1, innerUrl2);
               } catch (MalformedURLException var11) {
                  return super.sameFile(url1, url2);
               }
            }
         } else {
            return super.sameFile(url1, url2);
         }
      } else {
         return false;
      }
   }

   static int indexOfSeparator(String spec) {
      return indexOfSeparator(spec, 0, spec.length());
   }

   static int indexOfSeparator(String spec, int start, int limit) {
      for(int i = limit - 1; i >= start; --i) {
         if (spec.charAt(i) == '!' && i + 1 < limit && spec.charAt(i + 1) == '/') {
            return i;
         }
      }

      return -1;
   }

   public static void clearCache() {
      JarFileUrlKey.clearCache();
      JarUrlConnection.clearCache();
   }
}
