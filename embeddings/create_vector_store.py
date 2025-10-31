import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import chromadb
from chromadb.utils import embedding_functions


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Chroma vector store from chunks and optional cached embeddings")
    parser.add_argument(
        "--chunks",
        default=str(Path(__file__).resolve().parent / "chunks.json"),
        help="Path to chunks.json",
    )
    parser.add_argument(
        "--persist_dir",
        default=str(Path(__file__).resolve().parent / "vector_store"),
        help="Chroma persist directory",
    )
    parser.add_argument("--collection", default="nephrology_ref")
    parser.add_argument(
        "--model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="SentenceTransformers model name",
    )
    parser.add_argument(
        "--embeddings",
        default=str(Path(__file__).resolve().parent / "embeddings.npy"),
        help="Optional precomputed embeddings .npy (if exists will be used)",
    )
    parser.add_argument(
        "--ids",
        default=str(Path(__file__).resolve().parent / "ids.json"),
        help="Optional ids.json for precomputed embeddings",
    )
    args = parser.parse_args()

    with open(args.chunks, "r", encoding="utf-8") as f:
        chunks: List[Dict[str, Any]] = json.load(f)
    texts = [c.get("text", "") for c in chunks]
    metadatas = [{k: v for k, v in c.items() if k != "text"} for c in chunks]
    ids = [c.get("id", str(i)) for i, c in enumerate(chunks)]

    client = chromadb.PersistentClient(path=args.persist_dir)

    # If we have cached embeddings, use them
    use_cached = os.path.exists(args.embeddings) and os.path.exists(args.ids)
    if use_cached:
        cached_ids = json.load(open(args.ids, "r", encoding="utf-8"))
        if len(cached_ids) == len(ids) and cached_ids == ids:
            embeddings = np.load(args.embeddings)
            collection = client.get_or_create_collection(name=args.collection)
            collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings.tolist())
            print(f"Added {len(ids)} items to collection '{args.collection}' with cached embeddings.")
            return

    # Fallback to on-the-fly embedding function
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=args.model)
    collection = client.get_or_create_collection(name=args.collection, embedding_function=embed_fn)
    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    print(f"Added {len(ids)} items to collection '{args.collection}' with on-the-fly embeddings.")


if __name__ == "__main__":
    main()


