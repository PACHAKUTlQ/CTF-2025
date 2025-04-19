package org.springframework.boot.loader.launch;

import java.util.Iterator;
import java.util.List;
import org.springframework.boot.loader.jarmode.JarMode;
import org.springframework.boot.loader.jarmode.JarModeErrorException;
import org.springframework.core.io.support.SpringFactoriesLoader;
import org.springframework.util.ClassUtils;

final class JarModeRunner {
   static final String DISABLE_SYSTEM_EXIT = JarModeRunner.class.getName() + ".DISABLE_SYSTEM_EXIT";
   static final String SUPPRESSED_SYSTEM_EXIT_CODE = JarModeRunner.class.getName() + ".SUPPRESSED_SYSTEM_EXIT_CODE";

   private JarModeRunner() {
   }

   static void main(String[] args) {
      String mode = System.getProperty("jarmode");
      boolean disableSystemExit = Boolean.getBoolean(DISABLE_SYSTEM_EXIT);

      try {
         runJarMode(mode, args);
         if (disableSystemExit) {
            System.setProperty(SUPPRESSED_SYSTEM_EXIT_CODE, "0");
         }
      } catch (Throwable var4) {
         printError(var4);
         if (disableSystemExit) {
            System.setProperty(SUPPRESSED_SYSTEM_EXIT_CODE, "1");
            return;
         }

         System.exit(1);
      }

   }

   private static void runJarMode(String mode, String[] args) {
      List<JarMode> candidates = SpringFactoriesLoader.loadFactories(JarMode.class, ClassUtils.getDefaultClassLoader());
      Iterator var3 = candidates.iterator();

      JarMode candidate;
      do {
         if (!var3.hasNext()) {
            throw new JarModeErrorException("Unsupported jarmode '" + mode + "'");
         }

         candidate = (JarMode)var3.next();
      } while(!candidate.accepts(mode));

      candidate.run(mode, args);
   }

   private static void printError(Throwable ex) {
      if (ex instanceof JarModeErrorException) {
         String message = ex.getMessage();
         System.err.println("Error: " + message);
         System.err.println();
      } else {
         ex.printStackTrace();
      }
   }
}
