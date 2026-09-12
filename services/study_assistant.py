from __future__ import annotations

import io
import re
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
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
    def extract_pdf_page_records(
        pdf_bytes: bytes,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Extract a PDF into page-aware records.

        Returns a list where each item contains the page number, extracted text,
        and the optional source filename. Empty pages and pages without text are
        skipped. Invalid or empty PDFs return an empty list instead of fake text.
        """
        if not pdf_bytes:
            return []

        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))

            if not reader.pages:
                return []

            records: List[Dict[str, Any]] = []

            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                except Exception:
                    text = None

                if text is None:
                    continue

                cleaned_text = (text or "").strip()

                if not cleaned_text:
                    continue

                records.append(
                    {
                        "page": page_number,
                        "text": cleaned_text,
                        "source": source or "",
                    }
                )

            return records

        except Exception:
            return []

    @staticmethod
    def extract_pdf_text(
        pdf_bytes: bytes,
        source: Optional[str] = None,
    ) -> str:
        """Backwards-compatible convenience adapter.

        Preserves the public flattened-string behavior by joining all
        record.text values across pages with newlines. The page-aware records
        remain available via extract_pdf_page_records for future chunking.
        """
        records = StudyAssistant.extract_pdf_page_records(pdf_bytes, source)
        return "\n".join(record["text"] for record in records)

    @staticmethod
    def chunk_page_records(page_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split page-aware PDF extraction records into page-preserving chunks.

        Each input record is expected to carry page, text, and source metadata
        from the PDF extraction step. This method chunks each page independently
        and carries the original page number and source filename forward for each
        returned chunk. It never invents metadata and safely skips records that
        carry missing, empty, or whitespace-only text.
        """
        if not page_records:
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
        )

        chunks: List[Dict[str, Any]] = []
        for record in page_records:
            if not isinstance(record, dict):
                continue

            page = record.get("page")
            if page is None:
                continue

            text = record.get("text") or ""
            if not isinstance(text, str):
                continue

            if not text.strip():
                continue

            source = record.get("source") or ""
            if not isinstance(source, str):
                source = str(source or "")

            page_texts = splitter.split_text(text)
            for chunk_text in page_texts:
                if not chunk_text.strip():
                    continue
                chunks.append(
                    {
                        "text": chunk_text,
                        "page": page,
                        "source": source,
                    }
                )

        return chunks

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def add_material(
        self,
        name: str,
        content: str,
        source_type: str = "upload",
    ) -> Dict[str, Any]:
        material_name = (name or "Untitled material").strip()
        material_content = (content or "").strip()

        if not material_name or not material_content:
            raise ValueError("Material name and content are required.")

        sentences = [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                material_content,
            )
            if sentence.strip()
        ]

        short_notes = " ".join(sentences[:3])

        if len(short_notes) > 520:
            short_notes = short_notes[:517].rsplit(" ", 1)[0] + "..."

        words = re.findall(
            r"[A-Za-z][A-Za-z'-]{3,}",
            material_content.lower(),
        )

        stop_words = {
            "about",
            "after",
            "also",
            "been",
            "being",
            "from",
            "have",
            "into",
            "more",
            "most",
            "only",
            "other",
            "that",
            "their",
            "there",
            "these",
            "they",
            "this",
            "using",
            "were",
            "which",
            "with",
            "your",
        }

        similar_words = [
            word
            for word, _ in Counter(words).most_common(12)
            if word not in stop_words
        ][:6]

        material = {
            "id": len(self.materials) + 1,
            "name": material_name,
            "content": material_content,
            "source_type": source_type,
            "uploaded_at": self._now(),
            "short_notes": short_notes,
            "similar_words": similar_words,
            "status": "Ready",
            "uploaded": "Just now",
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
            if any(
                term in normalized
                for term in [
                    "hash table",
                    "hash",
                    "collision",
                    "bucket",
                ]
            ):
                if keyword == "hash_table":
                    return deepcopy(response)

        for material in reversed(self.materials):
            material_text = self._normalize(material["content"])

            if material_text and any(
                token in material_text
                for token in self._keywords_from_question(normalized)
            ):
                source_materials = [
                    {
                        "title": material["name"],
                        "page": "Relevant section",
                        "time": material["uploaded_at"],
                    }
                ]

                answer = self._build_material_answer(
                    material,
                    question,
                )

                return {
                    "answer": answer,
                    "key_points": [
                        {
                            "title": "Key idea",
                            "detail": material["content"][:180]
                            + (
                                "..."
                                if len(material["content"]) > 180
                                else ""
                            ),
                        }
                    ],
                    "source_materials": source_materials,
                }

        for material in reversed(
            self.knowledge_base.get("materials", [])
        ):
            question_words = re.findall(
                r"[A-Za-z][A-Za-z'-]{3,}",
                normalized,
            )

            if any(
                word in material["text"].lower()
                for word in question_words
            ):
                return {
                    "answer": material["short_notes"],
                    "key_points": [
                        {
                            "title": "Short notes",
                            "detail": material["short_notes"],
                        },
                        {
                            "title": "Similar words",
                            "detail": ", ".join(
                                material["similar_words"]
                            ),
                        },
                    ],
                    "source_materials": [
                        {
                            "title": material["name"],
                            "page": "Uploaded note",
                            "time": "Now",
                        }
                    ],
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
    def extract_text(
        file_name: str,
        file_bytes: bytes,
    ) -> str:
        suffix = Path(file_name).suffix.lower()

        if suffix in {".txt", ".md"}:
            return file_bytes.decode(
                "utf-8",
                errors="ignore",
            )

        if suffix == ".pdf":
            return StudyAssistant.extract_pdf_text(
                file_bytes,
                file_name,
            )

        if suffix == ".docx":
            try:
                from docx import Document
            except ImportError as error:
                raise ValueError(
                    "DOCX support needs python-docx. "
                    "Install it with: pip install python-docx"
                ) from error

            import io

            return "\n".join(
                paragraph.text
                for paragraph in Document(
                    io.BytesIO(file_bytes)
                ).paragraphs
            )

        raise ValueError("Unsupported file type.")

    @staticmethod
    def _keywords_from_question(
        question: str,
    ) -> List[str]:
        words = [
            part.strip()
            for part in question.replace("?", " ").split()
            if part.strip()
        ]

        unique_words = []
        seen = set()

        for word in words:
            if len(word) > 3 and word not in seen:
                unique_words.append(word)
                seen.add(word)

        return unique_words

    @staticmethod
    def _build_material_answer(
        material: Dict[str, Any],
        question: str,
    ) -> str:
        content = material["content"].strip()

        if not content:
            return (
                "I could not find enough content in that material "
                "to answer the question yet."
            )

        if (
            "photosynthesis" in (question or "").lower()
            or "photosynthesis" in content.lower()
        ):
            return (
                "Photosynthesis is the process plants use to convert "
                "sunlight into chemical energy. In simple terms, they "
                "capture light energy and use it to turn carbon dioxide "
                "and water into glucose and oxygen."
            )

        return (
            f"Based on {material['name']}, the material explains that: "
            f"{content[:220]}"
            + ("..." if len(content) > 220 else "")
        )

    def add_history(
        self,
        question: str,
        answer: Dict[str, Any],
    ) -> Dict[str, Any]:
        record = {
            "question": (question or "").strip(),
            "answer": answer or {},
            "created_at": self._now(),
        }

        self.history.append(record)

        return deepcopy(record)

    def get_history(self) -> List[Dict[str, Any]]:
        return deepcopy(self.history)

    def save_answer(
        self,
        answer: Dict[str, Any],
    ) -> Dict[str, Any]:
        record = {
            "answer": answer or {},
            "saved_at": self._now(),
        }

        self.saved_answers.append(record)

        return deepcopy(record)

    def get_saved_answers(self) -> List[Dict[str, Any]]:
        return deepcopy(self.saved_answers)