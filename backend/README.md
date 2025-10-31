Medical AI Assistant - Backend

Setup
- Python 3.10+
- Create venv, install requirements:
  - python -m venv .venv && .venv/Scripts/activate (Windows)
  - pip install -r requirements.txt

Run
- uvicorn app.main:app --reload --port 8000

Endpoints
- GET /patients/lookup?name=John
- POST /rag/query { query, top_k }
- POST /search/web { query, max_results }
- POST /chat/session { session_id?, message, patient_name? }
- GET /health

Notes
- Patient DB auto-seeded to patient_data/patient_reports.json (>=25 records)
- RAG uses Chroma DB with SentenceTransformers. Provide embeddings/chunks.json or populate at runtime.
- Logs appended to logs/agent_audit.json and logs/error.log


