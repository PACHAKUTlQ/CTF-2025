package org.springframework.boot.loader.net.protocol.jar;

import java.io.File;
import java.io.IOException;
import java.lang.Runtime.Version;
import java.util.function.Consumer;
import java.util.jar.JarFile;
import java.util.jar.Manifest;
import java.util.zip.ZipEntry;
import org.springframework.boot.loader.ref.Cleaner;

class UrlJarFile extends JarFile {
   private final UrlJarManifest manifest;
   private final Consumer<JarFile> closeAction;

   UrlJarFile(File file, Version version, Consumer<JarFile> closeAction) throws IOException {
      super(file, true, 1, version);
      Cleaner.instance.register(this, (Runnable)null);
      this.manifest = new UrlJarManifest(() -> {
         return super.getManifest();
      });
      this.closeAction = closeAction;
   }

   public ZipEntry getEntry(String name) {
      return UrlJarEntry.of(super.getEntry(name), this.manifest);
   }

   public Manifest getManifest() throws IOException {
      return this.manifest.get();
   }

   public void close() throws IOException {
      if (this.closeAction != null) {
         this.closeAction.accept(this);
      }

      super.close();
   }
}
