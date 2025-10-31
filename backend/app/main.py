from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import (
    PatientLookupResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    WebSearchRequest,
    WebSearchResponse,
    ChatRequest,
    ChatResponse,
)
from .patient_utils import lookup_patient_by_name, load_patient_reports
from .rag_retriever import RAGRetriever
from .web_search import web_search
from .agent_orchestration import handle_chat
from .logging_utils import log_error


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = RAGRetriever()


@app.get("/patients/lookup", response_model=PatientLookupResponse)
def patients_lookup(name: str = Query(..., description="Patient name substring match")):
    try:
        matches = lookup_patient_by_name(name)
        if not matches:
            return PatientLookupResponse(status="not_found", matches=[], message="No patient found")
        if len(matches) > 1:
            return PatientLookupResponse(status="multiple", matches=matches, message="Multiple matches")
        return PatientLookupResponse(status="ok", matches=matches)
    except Exception as e:
        log_error("patients_lookup failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal error")


@app.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(body: RAGQueryRequest):
    try:
        retrieved = retriever.retrieve(body.query, top_k=body.top_k)
        if retrieved:
            citations = []
            for r in retrieved:
                meta = r.get("metadata", {})
                citations.append({"page": meta.get("page"), "section": meta.get("section"), "score": r.get("distance")})
            context = "\n\n".join([r.get("text", "") for r in retrieved[:3]])
            # Inline formatted citations (first 3)
            cite_labels = []
            for c in citations[:3]:
                parts = []
                if c.get("section"):
                    parts.append(str(c["section"]))
                if c.get("page"):
                    parts.append(f"p. {c['page']}")
                cite_labels.append("; ".join(parts) if parts else "reference")
            inline_cites = ", ".join([f"[{s}]" for s in cite_labels]) if cite_labels else ""
            answer = f"From reference {inline_cites}:\n{context}"
            return RAGQueryResponse(answer=answer, citations=citations, retrieved_chunks=retrieved)
        return RAGQueryResponse(answer="No relevant context found.", citations=[], retrieved_chunks=[])
    except Exception as e:
        log_error("rag_query failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal error")


@app.post("/search/web", response_model=WebSearchResponse)
def search_web(body: WebSearchRequest):
    try:
        results = web_search(body.query, body.max_results)
        return WebSearchResponse(results=results)
    except Exception as e:
        log_error("search_web failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal error")


@app.post("/chat/session", response_model=ChatResponse)
def chat_session(body: ChatRequest):
    try:
        return handle_chat(body.session_id, body.message, body.patient_name)
    except Exception as e:
        log_error("chat_session failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal error")


@app.get("/health")
def health():
    # touch patient db to ensure seeded
    _ = load_patient_reports()
    return {"status": "ok", "app": settings.app_name}


@app.get("/logs/agent")
def get_agent_logs(download: bool = False):
    try:
        path = settings.agent_audit_log_path
        if download:
            return FileResponse(path=path, media_type="text/plain", filename="agent_audit.ndjson")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return PlainTextResponse(content, media_type="text/plain")
    except FileNotFoundError:
        return PlainTextResponse("", media_type="text/plain")
    except Exception as e:
        log_error("get_agent_logs failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal error")


