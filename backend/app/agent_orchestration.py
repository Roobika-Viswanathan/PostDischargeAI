import uuid
from datetime import datetime
from typing import Dict, Any, Tuple

from .schemas import ChatSessionState, ChatTurn, ChatResponse, PatientReport, RAGQueryResponse, Citation
from .patient_utils import lookup_patient_by_name
from .rag_retriever import RAGRetriever
from .web_search import web_search
from .logging_utils import log_agent_event


SESSIONS: Dict[str, ChatSessionState] = {}
retriever = RAGRetriever()


def get_or_create_session(session_id: str | None) -> ChatSessionState:
    if session_id and session_id in SESSIONS:
        return SESSIONS[session_id]
    sid = session_id or str(uuid.uuid4())
    state = ChatSessionState(session_id=sid, history=[])
    SESSIONS[sid] = state
    return state


def receptionist_handle(state: ChatSessionState, message: str, patient_name: str | None) -> Tuple[str, str | None]:
    # Greeting and patient identification
    if state.patient_report is None:
        # Try to identify patient
        if not patient_name:
            return (
                "Hello! I'm your post-discharge assistant. May I have your full name to pull your report?",
                None,
            )
        matches = lookup_patient_by_name(patient_name)
        if not matches:
            log_agent_event({"type": "patient_lookup", "result": "not_found", "query": patient_name})
            return (f"I couldn't find a patient matching '{patient_name}'. Could you recheck the spelling?", None)
        if len(matches) > 1:
            names = ", ".join(sorted({m.patient_name for m in matches}))
            log_agent_event({"type": "patient_lookup", "result": "multiple", "query": patient_name, "candidates": names})
            return (f"I found multiple matches: {names}. Please confirm your full name.", None)
        state.patient_report = matches[0]
        log_agent_event({"type": "patient_lookup", "result": "success", "patient_name": state.patient_report.patient_name})
        summary = (
            f"Thanks, {state.patient_report.patient_name}. Your primary diagnosis is "
            f"{state.patient_report.diagnosis}. Follow-up: "
            f"{'; '.join(state.patient_report.follow_up_instructions)}.\n"
            "Have you been able to take your medications as prescribed? Any new symptoms?"
        )
        return (summary, None)

    # Route medical queries to clinical agent based on simple heuristic
    medical_keywords = ["pain", "swelling", "shortness", "medication", "dose", "kidney", "urine", "bp", "diet", "potassium", "phosphorus"]
    if any(k in message.lower() for k in medical_keywords):
        return ("Routing to clinical agent for a detailed response.", "clinical")
    return (
        "I can help with scheduling, updating info, or passing your medical questions to our clinical AI.",
        None,
    )


def clinical_handle(state: ChatSessionState, message: str) -> Tuple[str, RAGQueryResponse | None]:
    # RAG over nephrology reference, fallback to web
    retrieved = retriever.retrieve(message)
    citations = []
    for r in retrieved:
        meta = r.get("metadata", {})
        citations.append(Citation(page=meta.get("page"), section=meta.get("section"), score=r.get("distance")))
    if retrieved:
        context_snippets = "\n\n".join([r.get("text", "") for r in retrieved[:3]])
        # Build inline citation strings
        citation_strs = []
        for c in citations[:3]:
            parts = []
            if c.section:
                parts.append(str(c.section))
            if c.page:
                parts.append(f"p. {c.page}")
            citation_strs.append("; ".join(parts) if parts else "reference")
        inline_cites = ", ".join([f"[{s}]" for s in citation_strs]) if citation_strs else ""

        answer = (
            f"Based on nephrology reference {inline_cites}:\n{context_snippets}\n\n"
            "Let me know if you want more detail or guidance tailored to your meds and labs."
        )
        rag = RAGQueryResponse(answer=answer, citations=citations, retrieved_chunks=retrieved)
        log_agent_event({"type": "rag_query", "results": len(retrieved)})
        return (answer, rag)

    # Fallback web search
    web = web_search(message)
    if web:
        top = web[0]
        answer = (
            f"I couldn't find this in the nephrology reference. Here's something relevant online: {top.title} ({top.url})."
        )
        log_agent_event({"type": "web_search", "results": len(web)})
        return (answer, None)
    return ("I'm sorry, I couldn't find relevant information. Please consult your provider.", None)


def handle_chat(session_id: str | None, message: str, patient_name: str | None) -> ChatResponse:
    state = get_or_create_session(session_id)
    state.history.append(ChatTurn(role="user", content=message, timestamp=datetime.utcnow()))

    receptionist_msg, handoff = receptionist_handle(state, message, patient_name)
    if handoff == "clinical":
        clinical_answer, rag = clinical_handle(state, message)
        state.history.append(ChatTurn(role="assistant", content=clinical_answer, timestamp=datetime.utcnow()))
        log_agent_event({"type": "handoff", "from": "receptionist", "to": "clinical", "reason": "medical_query"})
        return ChatResponse(
            session_id=state.session_id,
            response=clinical_answer,
            agent="clinical",
            handoff="receptionist->clinical",
            citations=rag.citations if rag else [],
        )

    state.history.append(ChatTurn(role="assistant", content=receptionist_msg, timestamp=datetime.utcnow()))
    return ChatResponse(session_id=state.session_id, response=receptionist_msg, agent="receptionist", handoff=None, citations=[])


