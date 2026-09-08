from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


class StudyAssistant:
    """Simple backend for a study assistant that answers questions from uploaded course material."""

    def __init__(self, knowledge_base: Optional[Dict[str, Any]] = None) -> None:
        self.knowledge_base = knowledge_base or {
            "hash_table": {
                "answer": (
                    "A hash table is a data structure that stores values using a key. "
                    "The key is passed through a hash function, which turns it into an integer "
                    "index in an array. This makes lookup efficient because the table can jump "
                    "directly to the right bucket."
                ),
                "key_points": [
                    {
                        "title": "Hash Function",
                        "detail": "Converts a key (like a string) into an integer index.",
                    },
                    {
                        "title": "Buckets",
                        "detail": "The array where values are stored.",
                    },
                    {
                        "title": "Collisions",
                        "detail": "Happen when two different keys generate the same index; they are handled by chaining or open addressing.",
                    },
                ],
                "source_materials": [
                    {
                        "title": "Data Structures Notes.pdf",
                        "page": "Page 42",
                        "time": "2 days ago",
                    }
                ],
            }
        }

    def answer_question(self, question: str) -> Dict[str, Any]:
        normalized = (question or "").strip().lower()

        if not normalized:
            return {
                "answer": "Please ask a question about your study materials.",
                "key_points": [],
                "source_materials": [],
            }

        if any(keyword in normalized for keyword in ["hash table", "hash", "collision", "bucket"]):
            return self.knowledge_base["hash_table"]

        for material in reversed(self.knowledge_base.get("materials", [])):
            question_words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", normalized)
            if any(word in material["text"].lower() for word in question_words):
                return {
                    "answer": material["short_notes"],
                    "key_points": [
                        {"title": "Short notes", "detail": material["short_notes"]},
                        {"title": "Similar words", "detail": ", ".join(material["similar_words"])},
                    ],
                    "source_materials": [{"title": material["name"], "page": "Uploaded note", "time": "Now"}],
                }

        return {
            "answer": (
                "I could not find a direct match in your uploaded study material. "
                "Please ask about the specific topic from your lecture notes or upload the relevant file."
            ),
            "key_points": [
                {
                    "title": "Hint",
                    "detail": "Try asking about a specific concept, chapter, or formula from your notes.",
                }
            ],
            "source_materials": [],
        }

    def add_material(self, name: str, text: str) -> Dict[str, Any]:
        """Create useful local study notes without requiring an external AI key."""
        clean_text = re.sub(r"\s+", " ", text or "").strip()
        if not clean_text:
            raise ValueError("This file does not contain readable text.")

        sentences = re.split(r"(?<=[.!?])\s+", clean_text)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        short_notes = " ".join(sentences[:3])
        if len(short_notes) > 520:
            short_notes = short_notes[:517].rsplit(" ", 1)[0] + "..."

        words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", clean_text.lower())
        stop_words = {
            "about", "after", "also", "been", "being", "from", "have", "into",
            "more", "most", "only", "other", "that", "their", "there", "these",
            "they", "this", "using", "were", "which", "with", "your",
        }
        similar_words = [word for word, _ in Counter(words).most_common(12) if word not in stop_words][:6]
        material = {"name": name, "text": clean_text, "short_notes": short_notes, "similar_words": similar_words}
        self.knowledge_base.setdefault("materials", []).append(material)
        return material

    @staticmethod
    def extract_text(file_name: str, file_bytes: bytes) -> str:
        suffix = Path(file_name).suffix.lower()
        if suffix in {".txt", ".md"}:
            return file_bytes.decode("utf-8", errors="ignore")
        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as error:
                raise ValueError("PDF support needs the pypdf package. Install it with: pip install pypdf") from error
            import io
            return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(file_bytes)).pages)
        if suffix == ".docx":
            try:
                from docx import Document
            except ImportError as error:
                raise ValueError("DOCX support needs python-docx. Install it with: pip install python-docx") from error
            import io
            return "\n".join(paragraph.text for paragraph in Document(io.BytesIO(file_bytes)).paragraphs)
        raise ValueError("Unsupported file type.")
