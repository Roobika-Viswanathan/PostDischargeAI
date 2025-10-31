import os
from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "Medical AI Assistant")
    environment: str = os.getenv("ENVIRONMENT", "dev")

    # Vector store / embeddings
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    vector_store_dir: str = os.getenv("VECTOR_STORE_DIR", str(BASE_DIR / "embeddings" / "vector_store"))
    pdf_chunks_path: str = os.getenv("PDF_CHUNKS_PATH", str(BASE_DIR / "embeddings" / "chunks.json"))

    # Patient data
    patient_reports_path: str = os.getenv("PATIENT_REPORTS_PATH", str(BASE_DIR / "patient_data" / "patient_reports.json"))
    min_patient_records: int = int(os.getenv("MIN_PATIENT_RECORDS", "25"))

    # Logging
    agent_audit_log_path: str = os.getenv("AGENT_AUDIT_LOG_PATH", str(BASE_DIR / "logs" / "agent_audit.json"))
    error_log_path: str = os.getenv("ERROR_LOG_PATH", str(BASE_DIR / "logs" / "error.log"))

    # Retrieval
    num_retrieval_results: int = int(os.getenv("NUM_RETRIEVAL_RESULTS", "4"))
    min_chunk_words: int = int(os.getenv("MIN_CHUNK_WORDS", "300"))
    max_chunk_words: int = int(os.getenv("MAX_CHUNK_WORDS", "500"))

    # Web search
    web_search_results: int = int(os.getenv("WEB_SEARCH_RESULTS", "5"))


settings = Settings()


