import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const csvFilePath = path.resolve(__dirname, 'readers.csv')

// Ensure CSV file exists with header
if (!fs.existsSync(csvFilePath)) {
  fs.writeFileSync(
    csvFilePath,
    'Timestamp,Name,WhatsApp,Email,City\n',
    'utf-8'
  )
}

function csvMiddlewarePlugin() {
  return {
    name: 'csv-registration-api',
    configureServer(server) {
      server.middlewares.use('/api/register', (req, res, next) => {
        if (req.method !== 'POST') {
          res.statusCode = 405
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ error: 'Method Not Allowed' }))
          return
        }

        let body = ''
        req.on('data', (chunk) => {
          body += chunk
        })

        req.on('end', () => {
          try {
            const data = JSON.parse(body || '{}')
            const { name = '', whatsapp = '', email = '', city = '' } = data

            if (!name.trim() || !whatsapp.trim() || !email.trim() || !city.trim()) {
              res.statusCode = 400
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ error: 'All fields are required.' }))
              return
            }

            const cleanField = (val) => {
              const str = String(val).replace(/"/g, '""').trim()
              return `"${str}"`
            }

            const timestamp = new Date().toISOString()
            const row = `${cleanField(timestamp)},${cleanField(name)},${cleanField(whatsapp)},${cleanField(email)},${cleanField(city)}\n`

            fs.appendFileSync(csvFilePath, row, 'utf-8')

            res.statusCode = 200
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ success: true, message: 'Registration recorded.' }))
          } catch (err) {
            console.error('CSV Write Error:', err)
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: 'Failed to write registration to CSV.' }))
          }
        })
      })
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), csvMiddlewarePlugin()],
})
