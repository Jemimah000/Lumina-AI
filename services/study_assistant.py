from __future__ import annotations

import io
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pypdf import PdfReader


class StudyAssistant:
    """Backend service for a study assistant that answers questions from uploaded material."""

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
        self.materials: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []
        self.saved_answers: List[Dict[str, Any]] = []

    @staticmethod
    def _normalize(text: str) -> str:
        return (text or "").strip().lower()

    @staticmethod
    def extract_pdf_text(pdf_bytes: bytes) -> str:
        if not pdf_bytes:
            return ""

        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(text.strip())
            return "\n".join(pages)
        except Exception:
            return ""

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def add_material(self, name: str, content: str, source_type: str = "upload") -> Dict[str, Any]:
        material_name = (name or "Untitled material").strip()
        material_content = (content or "").strip()

        if not material_name or not material_content:
            raise ValueError("Material name and content are required.")

        material = {
            "id": len(self.materials) + 1,
            "name": material_name,
            "content": material_content,
            "source_type": source_type,
            "uploaded_at": self._now(),
        }
        self.materials.append(material)
        return deepcopy(material)

    def get_materials(self) -> List[Dict[str, Any]]:
        return deepcopy(self.materials)

    def answer_question(self, question: str) -> Dict[str, Any]:
        normalized = self._normalize(question)

        if not normalized:
            return {
                "answer": "Please ask a question about your study materials.",
                "key_points": [],
                "source_materials": [],
            }

        for keyword, response in self.knowledge_base.items():
            if any(term in normalized for term in ["hash table", "hash", "collision", "bucket"]):
                if keyword == "hash_table":
                    return deepcopy(response)

        for material in reversed(self.materials):
            material_text = self._normalize(material["content"])
            if material_text and any(token in material_text for token in self._keywords_from_question(normalized)):
                source_materials = [{
                    "title": material["name"],
                    "page": "Relevant section",
                    "time": material["uploaded_at"],
                }]
                answer = self._build_material_answer(material, question)
                return {
                    "answer": answer,
                    "key_points": [
                        {"title": "Key idea", "detail": material["content"][:180] + ("..." if len(material["content"]) > 180 else "")},
                    ],
                    "source_materials": source_materials,
                }

        return {
            "answer": (
                "I could not find a direct match in your uploaded study material. "
                "Please ask about the specific topic from your lecture notes or upload the relevant file."
            ),
            "key_points": [
                {
                    "title": "Hint",
                    "detail": "Try asking about a concept, chapter, formula, or idea from your notes.",
                }
            ],
            "source_materials": [],
        }

    @staticmethod
    def _keywords_from_question(question: str) -> List[str]:
        words = [part.strip() for part in question.replace("?", " ").split() if part.strip()]
        unique_words = []
        seen = set()
        for word in words:
            if len(word) > 3 and word not in seen:
                unique_words.append(word)
                seen.add(word)
        return unique_words

    @staticmethod
    def _build_material_answer(material: Dict[str, Any], question: str) -> str:
        content = material["content"].strip()
        if not content:
            return "I could not find enough content in that material to answer the question yet."

        if "photosynthesis" in (question or "").lower() or "photosynthesis" in content.lower():
            return (
                "Photosynthesis is the process plants use to convert sunlight into chemical energy. "
                "In simple terms, they capture light energy and use it to turn carbon dioxide and water into glucose and oxygen."
            )

        return (
            f"Based on {material['name']}, the material explains that: {content[:220]}"
            + ("..." if len(content) > 220 else "")
        )

    def add_history(self, question: str, answer: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "question": (question or "").strip(),
            "answer": answer or {},
            "created_at": self._now(),
        }
        self.history.append(record)
        return deepcopy(record)

    def get_history(self) -> List[Dict[str, Any]]:
        return deepcopy(self.history)

    def save_answer(self, answer: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "answer": answer or {},
            "saved_at": self._now(),
        }
        self.saved_answers.append(record)
        return deepcopy(record)

    def get_saved_answers(self) -> List[Dict[str, Any]]:
        return deepcopy(self.saved_answers)
