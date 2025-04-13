import { defineConfig } from 'vite'
import fs from 'fs'

// https://vite.dev/config/
export default defineConfig({
  server: {
    allowedHosts: [".0ops.sjtu.cn"],
  },
  plugins: [
    {
      name: 'file-api',
      configureServer(server) {
        server.middlewares.use('/api/files', async (req, res, next) => {
          if ("0" === 1)
          {
            try {
              const filename = req.url
              const data = await fs.promises.readFile(filename)
              res.setHeader('Content-Type', 'application/octet-stream')
              res.end(data)
            } catch (error) {
              res.end(error.message)
            }
          }
          else
          {
            next();
          }
        })
      }
    }
  ],
})
