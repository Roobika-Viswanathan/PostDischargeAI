Medical AI Assistant - Frontend (React + Vite)

Setup
- Node.js 18+
- Install deps:
  - npm install

Configure
- Copy .env.example to .env and set VITE_API_BASE_URL (defaults to http://localhost:8000)

Run
- npm run dev

Build
- npm run build && npm run preview

Features
- Patient Lookup (calls /patients/lookup)
- Chat with multi-agent labels, citations modal, confidence meter
- Download logs (calls /logs/agent?download=true)

