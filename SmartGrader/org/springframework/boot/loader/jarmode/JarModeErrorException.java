package org.springframework.boot.loader.jarmode;

public class JarModeErrorException extends RuntimeException {
   public JarModeErrorException(String message) {
      super(message);
   }

   public JarModeErrorException(String message, Throwable cause) {
      super(message, cause);
   }
}
