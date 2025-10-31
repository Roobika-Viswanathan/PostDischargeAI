import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import re

import fitz  # PyMuPDF


def guess_section_header(line: str) -> str | None:
    text = line.strip()
    if not text:
        return None
    if text.isupper() and len(text.split()) <= 10:
        return text
    if text.endswith(":") and len(text.split()) <= 10:
        return text[:-1]
    return None


def extract_pdf_text_with_meta(pdf_path: str) -> List[Dict[str, Any]]:
    doc = fitz.open(pdf_path)
    pages: List[Dict[str, Any]] = []
    for pno, page in enumerate(doc, start=1):
        text = page.get_text()
        pages.append({"page": pno, "text": text})
    return pages


def words_count(s: str) -> int:
    return len([w for w in s.split() if w])


def _split_into_sentences(text: str) -> List[str]:
    # Lightweight sentence splitter (avoid external deps)
    # Splits on ., !, ? followed by space and capital or end of line
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\(])", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_pages(
    pages: List[Dict[str, Any]],
    file_label: str,
    min_words: int = 300,
    max_words: int = 500,
    overlap_words: int = 60,
) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    current_section: str | None = None
    buffer_sentences: List[str] = []
    buffer_page: int | None = None
    chunk_idx = 0

    def buffer_word_len() -> int:
        return words_count(" ".join(buffer_sentences))

    for page in pages:
        page_num = page["page"]
        lines = page["text"].splitlines()

        # Detect potential section headers, but sentence-split per page
        page_text = []
        for line in lines:
            header = guess_section_header(line)
            if header:
                current_section = header
            page_text.append(line)
        sentences = _split_into_sentences(" ".join(page_text))

        for sent in sentences:
            candidate_words = words_count(sent)
            if buffer_page is None:
                buffer_page = page_num
            # If adding this sentence exceeds max, emit a chunk if >= min
            if buffer_word_len() + candidate_words > max_words and buffer_word_len() >= min_words:
                chunk_text = " ".join(buffer_sentences)
                chunks.append(
                    {
                        "id": f"{file_label}-p{buffer_page}-c{chunk_idx}",
                        "file": file_label,
                        "page": buffer_page,
                        "section": current_section,
                        "text": chunk_text,
                    }
                )
                chunk_idx += 1
                # Apply overlap by words (approximate by sentences)
                if overlap_words > 0:
                    # keep tail sentences until overlap satisfied
                    retained: List[str] = []
                    running = 0
                    for s in reversed(buffer_sentences):
                        w = words_count(s)
                        if running >= overlap_words:
                            break
                        retained.insert(0, s)
                        running += w
                    buffer_sentences = retained
                else:
                    buffer_sentences = []
                buffer_page = page_num

            buffer_sentences.append(sent)

        # At page end, if buffer is within limits, emit a chunk
        if min_words <= buffer_word_len() <= max_words:
            chunk_text = " ".join(buffer_sentences)
            chunks.append(
                {
                    "id": f"{file_label}-p{buffer_page}-c{chunk_idx}",
                    "file": file_label,
                    "page": buffer_page,
                    "section": current_section,
                    "text": chunk_text,
                }
            )
            chunk_idx += 1
            buffer_sentences = []
            buffer_page = None

    # Flush remainder
    if buffer_sentences:
        chunk_text = " ".join(buffer_sentences)
        chunks.append(
            {
                "id": f"{file_label}-tail-c{chunk_idx}",
                "file": file_label,
                "page": buffer_page,
                "section": current_section,
                "text": chunk_text,
            }
        )

    chunks = [c for c in chunks if words_count(c["text"]) >= max(50, min_words // 2)]
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PDF into chunked JSON for RAG")
    parser.add_argument("pdf", help="Path to nephrology reference PDF")
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent / "chunks.json"),
        help="Output chunks.json path",
    )
    parser.add_argument("--min_words", type=int, default=300)
    parser.add_argument("--max_words", type=int, default=500)
    parser.add_argument("--overlap_words", type=int, default=60)
    args = parser.parse_args()

    pdf_path = args.pdf
    file_label = Path(pdf_path).stem
    pages = extract_pdf_text_with_meta(pdf_path)
    chunks = chunk_pages(
        pages,
        file_label=file_label,
        min_words=args.min_words,
        max_words=args.max_words,
        overlap_words=args.overlap_words,
    )

    os.makedirs(Path(args.out).parent, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    print(f"Wrote {len(chunks)} chunks to {args.out}")


if __name__ == "__main__":
    main()


 