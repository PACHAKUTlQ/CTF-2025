package org.springframework.boot.loader.launch;

public class JarLauncher extends ExecutableArchiveLauncher {
   public JarLauncher() throws Exception {
   }

   protected JarLauncher(Archive archive) throws Exception {
      super(archive);
   }

   public static void main(String[] args) throws Exception {
      (new JarLauncher()).launch(args);
   }
}
