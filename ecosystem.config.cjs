const path = require('path')

const root = '/opt/sites/vedel'

module.exports = {
  apps: [
    {
      name: 'vedel',
      script: path.join(root, '.next/standalone/server.js'),
      cwd: path.join(root, '.next/standalone'),
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        PORT: '3002',
        HOSTNAME: '0.0.0.0',
        NEXT_TELEMETRY_DISABLED: '1',
        PRICE_SHEET_URL:
          'https://docs.google.com/spreadsheets/d/1p13kvy6wSne5sTlsVp_M5G_JU2pp1i7tDvImic11Nlk/export?format=csv',
        DJANGO_URL: 'http://127.0.0.1:8020',
      },
    },
  ],
}
