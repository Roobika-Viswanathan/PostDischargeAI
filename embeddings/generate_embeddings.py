import argparse
import json
import os
from pathlib import Path
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate embeddings for chunks.json")
    parser.add_argument(
        "--chunks",
        default=str(Path(__file__).resolve().parent / "chunks.json"),
        help="Path to chunks.json",
    )
    parser.add_argument(
        "--model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="SentenceTransformers model name",
    )
    parser.add_argument(
        "--out_dir",
        default=str(Path(__file__).resolve().parent),
        help="Output directory for embeddings and ids",
    )
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()

    with open(args.chunks, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    texts: List[str] = [c.get("text", "") for c in chunks]
    ids: List[str] = [c.get("id", str(i)) for i, c in enumerate(chunks)]

    model = SentenceTransformer(args.model)
    embeddings = model.encode(texts, batch_size=args.batch_size, convert_to_numpy=True, show_progress_bar=True)

    out_dir = Path(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    np.save(out_dir / "embeddings.npy", embeddings)
    with open(out_dir / "ids.json", "w", encoding="utf-8") as f:
        json.dump(ids, f)
    print(f"Saved embeddings to {out_dir / 'embeddings.npy'} and ids to {out_dir / 'ids.json'}")


if __name__ == "__main__":
    main()


