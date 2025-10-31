from typing import List, Dict, Any
import os
import json

import chromadb
from chromadb.utils import embedding_functions

from .config import settings


class RAGRetriever:
    def __init__(self) -> None:
        os.makedirs(settings.vector_store_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.vector_store_dir)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model_name
        )
        self.collection = self.client.get_or_create_collection(
            name="nephrology_ref",
            embedding_function=self.embedding_fn,
        )
        self._ensure_index_built()

    def _ensure_index_built(self) -> None:
        # If empty, try to load chunks.json and populate
        if self.collection.count() == 0 and os.path.exists(settings.pdf_chunks_path):
            with open(settings.pdf_chunks_path, "r", encoding="utf-8") as f:
                chunks: List[Dict[str, Any]] = json.load(f)
            ids = []
            texts = []
            metadatas = []
            for i, ch in enumerate(chunks):
                ids.append(f"chunk-{i}")
                texts.append(ch.get("text", ""))
                meta = {k: v for k, v in ch.items() if k != "text"}
                metadatas.append(meta)
            if texts:
                self.collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def retrieve(self, query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
        k = top_k or settings.num_retrieval_results
        results = self.collection.query(query_texts=[query], n_results=k)
        retrieved: List[Dict[str, Any]] = []
        # Results structure: ids, documents, metadatas, distances
        for idx in range(len(results.get("ids", [[]])[0])):
            retrieved.append(
                {
                    "id": results["ids"][0][idx],
                    "text": results["documents"][0][idx],
                    "metadata": results["metadatas"][0][idx],
                    "distance": results.get("distances", [[None]])[0][idx],
                }
            )
        return retrieved


