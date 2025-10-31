from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PatientReport(BaseModel):
    patient_name: str
    discharge_date: str
    diagnosis: str
    medications: List[str]
    dietary_restrictions: List[str]
    follow_up_instructions: List[str]
    warning_signs: List[str]
    discharge_instructions: List[str]


class PatientLookupResponse(BaseModel):
    status: str
    matches: List[PatientReport] = Field(default_factory=list)
    message: Optional[str] = None


class RAGQueryRequest(BaseModel):
    query: str
    patient_context: Optional[PatientReport] = None
    top_k: Optional[int] = 4


class Citation(BaseModel):
    page: Optional[int] = None
    section: Optional[str] = None
    score: Optional[float] = None


class RAGQueryResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list)


class WebSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None


class WebSearchResponse(BaseModel):
    results: List[WebSearchResult]


class ChatTurn(BaseModel):
    role: str
    content: str
    timestamp: datetime


class ChatSessionState(BaseModel):
    session_id: str
    patient_report: Optional[PatientReport] = None
    history: List[ChatTurn] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    patient_name: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent: str
    handoff: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)


