from __future__ import annotations

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
