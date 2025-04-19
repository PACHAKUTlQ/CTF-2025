package org.springframework.boot.loader.net.protocol.nested;

import java.io.File;
import java.net.URI;
import java.net.URL;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.boot.loader.net.util.UrlDecoder;

public record NestedLocation(Path path, String nestedEntryName) {
   private static final Map<String, NestedLocation> locationCache = new ConcurrentHashMap();
   private static final Map<String, Path> pathCache = new ConcurrentHashMap();

   public NestedLocation(Path path, String nestedEntryName) {
      if (path == null) {
         throw new IllegalArgumentException("'path' must not be null");
      } else {
         this.path = path;
         this.nestedEntryName = nestedEntryName != null && !nestedEntryName.isEmpty() ? nestedEntryName : null;
      }
   }

   public static NestedLocation fromUrl(URL url) {
      if (url != null && "nested".equalsIgnoreCase(url.getProtocol())) {
         return parse(UrlDecoder.decode(url.toString().substring(7)));
      } else {
         throw new IllegalArgumentException("'url' must not be null and must use 'nested' protocol");
      }
   }

   public static NestedLocation fromUri(URI uri) {
      if (uri != null && "nested".equalsIgnoreCase(uri.getScheme())) {
         return parse(uri.getSchemeSpecificPart());
      } else {
         throw new IllegalArgumentException("'uri' must not be null and must use 'nested' scheme");
      }
   }

   static NestedLocation parse(String location) {
      if (location != null && !location.isEmpty()) {
         return (NestedLocation)locationCache.computeIfAbsent(location, (key) -> {
            return create(location);
         });
      } else {
         throw new IllegalArgumentException("'location' must not be empty");
      }
   }

   private static NestedLocation create(String location) {
      int index = location.lastIndexOf("/!");
      String locationPath = index != -1 ? location.substring(0, index) : location;
      String nestedEntryName = index != -1 ? location.substring(index + 2) : null;
      return new NestedLocation(!locationPath.isEmpty() ? asPath(locationPath) : null, nestedEntryName);
   }

   private static Path asPath(String locationPath) {
      return (Path)pathCache.computeIfAbsent(locationPath, (key) -> {
         return Path.of(!isWindows() ? locationPath : fixWindowsLocationPath(locationPath), new String[0]);
      });
   }

   private static boolean isWindows() {
      return File.separatorChar == '\\';
   }

   private static String fixWindowsLocationPath(String locationPath) {
      if (locationPath.length() > 2 && locationPath.charAt(2) == ':') {
         return locationPath.substring(1);
      } else {
         return locationPath.startsWith("///") && locationPath.charAt(4) == ':' ? locationPath.substring(3) : locationPath;
      }
   }

   static void clearCache() {
      locationCache.clear();
      pathCache.clear();
   }

   public Path path() {
      return this.path;
   }

   public String nestedEntryName() {
      return this.nestedEntryName;
   }
}
