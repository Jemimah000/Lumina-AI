import json
from pathlib import Path

import pytest

from services.study_assistant import StudyAssistant

import numpy as np


class FakeEmbeddingModel:
    def embed_documents(self, texts):
        return [[4.0, 5.0, 6.0] for _ in texts]

    def embed_query(self, text):
        return [4.0, 5.0, 6.0]


def build_pdf_from_page_texts(page_texts):
    """Create a tiny synthetic PDF with one encoded content stream per page.

    Page 1 and page 2 carry visible text; page 3 is intentionally empty and
    therefore should not create a page record from the extraction layer.
    """
    object_chunks = []

    # Catalog and pages tree.
    object_chunks.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    object_chunks.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R 5 0 R 7 0 R] /Count 3 >>\nendobj\n")

    # Shared font resource.
    object_chunks.append(b"8 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    # Page 1 with content stream object 4.
    stream_text = (
        "BT\n"
        "/F1 12 Tf\n"
        "50 100 Td\n"
        f"({page_texts[0]}) Tj\n"
        "ET\n"
    )
    stream_bytes = stream_text.encode("latin-1")
    object_chunks.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 4 0 R /Resources << /Font << /F1 8 0 R >> >> >>\nendobj\n"
    )
    object_chunks.append(
        f"4 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n{stream_text}\nendstream\nendobj\n".encode("latin-1")
    )

    # Page 2 with content stream object 6.
    stream_text = (
        "BT\n"
        "/F1 12 Tf\n"
        "50 100 Td\n"
        f"({page_texts[1]}) Tj\n"
        "ET\n"
    )
    stream_bytes = stream_text.encode("latin-1")
    object_chunks.append(
        b"5 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 6 0 R /Resources << /Font << /F1 8 0 R >> >> >>\nendobj\n"
    )
    object_chunks.append(
        f"6 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n{stream_text}\nendstream\nendobj\n".encode("latin-1")
    )

    # Page 3 intentionally blank page with no content stream, and therefore no extraction content.
    object_chunks.append(
        b"7 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 8 0 R >> >> >>\nendobj\n"
    )

    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for chunk in object_chunks:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(chunk)

    xref_start = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(object_chunks) + 1}\n".encode("ascii"))
    pdf_bytes.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf_bytes.extend(
        f"trailer\n<< /Size {len(object_chunks) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )

    return bytes(pdf_bytes)


def test_study_assistant_extracts_text_from_pdf_material():
    text = "Photosynthesis converts sunlight into chemical energy for plants."
    stream_text = (
        "BT\n"
        "/F1 12 Tf\n"
        "50 100 Td\n"
        f"({text}) Tj\n"
        "ET\n"
    )
    stream_bytes = stream_text.encode("latin-1")

    pdf_objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        b"4 0 obj\n<< /Length " + str(len(stream_bytes)).encode("ascii") + b" >>\nstream\n" + stream_bytes + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for chunk in pdf_objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(chunk)

    xref_start = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf_bytes.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf_bytes.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii"))

    assistant = StudyAssistant()
    extracted = assistant.extract_pdf_text(bytes(pdf_bytes))

    assert "photosynthesis" in extracted.lower()
    assert "chemical energy" in extracted.lower()


def test_extract_pdf_page_records_preserves_pages_and_safely_skips_empty_pages():
    pdf_bytes = build_pdf_from_page_texts([
        "Introduction to Formal Languages",
        "A grammar is a set of production rules.",
        "",
    ])

    records = StudyAssistant.extract_pdf_page_records(pdf_bytes, "Formal Languages Notes.pdf")

    assert len(records) == 2
    assert [record["page"] for record in records] == [1, 2]
    assert records[0]["text"] == "Introduction to Formal Languages"
    assert records[1]["text"] == "A grammar is a set of production rules."
    assert all(record["source"] == "Formal Languages Notes.pdf" for record in records)


def test_extract_pdf_page_records_handles_invalid_or_empty_pdf_input_safely():
    assert StudyAssistant.extract_pdf_page_records(b"", "Example.pdf") == []
    assert StudyAssistant.extract_pdf_page_records(b"not a valid pdf", "Example.pdf") == []


def test_answer_question_uses_faiss_retrieval_not_legacy_knowledge_base(monkeypatch, tmp_path):
    assistant = StudyAssistant(
        knowledge_base={"hash_table": {"answer": "legacy answer"}},
        storage_root=tmp_path / "data",
    )
    assistant.embedding_model = FakeEmbeddingModel()
    rag = assistant.build_faiss_index([{
        "text": "The uploaded notes define a stack as last in, first out.",
        "page": 2, "source": "notes.pdf", "embedding": [4.0, 5.0, 6.0],
    }])
    assistant.faiss_index, assistant.faiss_metadata = rag["index"], rag["metadata"]
    monkeypatch.setattr(assistant, "generate_answer", lambda question, chunks: "Grounded answer")

    result = assistant.answer_question("What is a stack?")

    assert result["answer"] == "Grounded answer"
    assert result["source_materials"] == [{"title": "notes.pdf", "page": 2}]


def test_study_assistant_tracks_uploads_history_and_saved_answers(tmp_path):
    assistant = StudyAssistant(storage_root=tmp_path / "data")
    material = assistant.add_material("Biology Notes", "Photosynthesis converts sunlight into chemical energy.")
    answer = {"answer": "Grounded answer", "source_materials": [{"title": material["name"], "page": 1}]}

    assert len(assistant.get_materials()) == 1

    assistant.add_history("What is photosynthesis?", answer)
    assistant.save_answer(answer)

    assert len(assistant.get_history()) == 1
    assert len(assistant.get_saved_answers()) == 1


def test_process_pdf_upload_runs_full_pipeline_and_saves_to_uploads(tmp_path):
    assistant = StudyAssistant(storage_root=tmp_path / "data")
    assistant.embedding_model = FakeEmbeddingModel()
    pdf_bytes = build_pdf_from_page_texts([
        "React is a library for building user interfaces.",
        "Components are reusable pieces of a user interface.",
        "",
    ])

    result = assistant.process_pdf_upload("React Notes.pdf", pdf_bytes)

    assert result["index"] is assistant.faiss_index
    assert result["index"].ntotal == 2
    assert {item["page"] for item in result["metadata"]} == {1, 2}
    assert all(item["source"] == "React Notes.pdf" for item in result["metadata"])
    materials = assistant.get_materials()
    assert len(materials) == 1 and materials[0]["status"] == "Ready"
    assert Path(materials[0]["file_path"]).parent == tmp_path / "data" / "uploads"


def test_answer_question_returns_exact_fallback_without_relevant_chunks(tmp_path):
    assistant = StudyAssistant(storage_root=tmp_path / "data")
    assistant.embedding_model = FakeEmbeddingModel()
    assert assistant.answer_question("What is unrelated?") == {
        "answer": "I couldn't find this information in the study material.",
        "key_points": [],
        "source_materials": [],
    }


def test_add_material_preserves_text_alias_for_ui_materials_list():
    assistant = StudyAssistant()
    material = assistant.add_material("Biology Notes", "Photosynthesis converts sunlight into chemical energy.")

    assert material["name"] == "Biology Notes"
    assert material["text"] == "Photosynthesis converts sunlight into chemical energy."
    assert material["content"] == "Photosynthesis converts sunlight into chemical energy."


def test_chunk_page_records_splits_long_pages_and_preserves_metadata():
    page_records = [
        {
            "page": 1,
            "text": "A " * 1200,
            "source": "sample.pdf",
        },
        {
            "page": 2,
            "text": "B " * 1200,
            "source": "sample.pdf",
        },
    ]

    chunks = StudyAssistant.chunk_page_records(page_records)

    assert len(chunks) > 1
    assert all(chunk["text"].strip() for chunk in chunks)
    assert all(chunk["source"] == "sample.pdf" for chunk in chunks)
    assert all(chunk["page"] == 1 for chunk in chunks if chunk["page"] == 1)
    assert all(chunk["page"] == 2 for chunk in chunks if chunk["page"] == 2)
    assert {chunk["page"] for chunk in chunks} == {1, 2}


def test_chunk_page_records_handles_empty_and_whitespace_inputs_safely():
    assert StudyAssistant.chunk_page_records([]) == []
    assert StudyAssistant.chunk_page_records([
        {"page": 1, "text": "   ", "source": "sample.pdf"},
    ]) == []
    assert StudyAssistant.chunk_page_records([
        {"page": 1, "text": "", "source": "sample.pdf"},
    ]) == []


def test_embed_chunks_produces_numeric_embeddings_and_preserves_metadata():
    assistant = StudyAssistant()
    assistant.embedding_model = FakeEmbeddingModel()

    chunks = [
        {"text": "Photosynthesis stores energy.", "page": 1, "source": "bio.pdf"},
        {"text": "Cells use ATP for reactions.", "page": 2, "source": "bio.pdf"},
    ]

    embedded = assistant.embed_chunks(chunks)

    assert len(embedded) == 2
    assert [item["text"] for item in embedded] == [chunk["text"] for chunk in chunks]
    assert [item["page"] for item in embedded] == [1, 2]
    assert [item["source"] for item in embedded] == ["bio.pdf", "bio.pdf"]
    assert all(isinstance(item["embedding"], list) for item in embedded)
    assert all(all(isinstance(value, (int, float)) for value in item["embedding"]) for item in embedded)


def test_embed_chunks_handles_empty_and_invalid_inputs_safely():
    assistant = StudyAssistant()
    assistant.embedding_model = FakeEmbeddingModel()

    assert assistant.embed_chunks([]) == []
    assert assistant.embed_chunks([
        {"text": "   ", "page": 1, "source": "bio.pdf"},
        {"text": "", "page": 2, "source": "bio.pdf"},
        {"text": "Valid text", "page": 3, "source": "bio.pdf"},
    ]) == [
        {
            "text": "Valid text",
            "page": 3,
            "source": "bio.pdf",
            "embedding": [4.0, 5.0, 6.0],
        }
    ]


def test_material_persistence_round_trip_and_duplicate_flow(tmp_path):
    storage_root = tmp_path / "data"
    upload_path = storage_root / "uploads" / "Frontend_Interview_Prep.pdf"
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"%PDF-1.4 synthetic sample")

    assistant = StudyAssistant(storage_root=storage_root)
    material = assistant.add_material(
        "Frontend_Interview_Prep.pdf",
        "React is a UI library used to build interfaces.",
        file_path=str(upload_path),
        file_hash="hash-frontend-interview-prep",
        page_count=8,
    )

    assert material["id"] == 1
    assert material["name"] == "Frontend_Interview_Prep.pdf"
    assert material["file_path"] == str(upload_path)
    assert material["status"] == "Ready"

    assistant2 = StudyAssistant(storage_root=storage_root)
    materials = assistant2.get_materials()
    assert len(materials) == 1
    assert materials[0]["name"] == "Frontend_Interview_Prep.pdf"
    assert materials[0]["file_path"] == str(upload_path)
    assert materials[0]["id"] == 1

    # Duplicate upload should update meaningfully and not add another record.
    assistant3 = StudyAssistant(storage_root=storage_root)
    material_dup = assistant3.add_material(
        "Frontend_Interview_Prep.pdf",
        "React is a UI library used to build interfaces.",
        file_path=str(upload_path),
        file_hash="hash-frontend-interview-prep",
        page_count=8,
    )
    assert len(assistant3.get_materials()) == 1
    assert material_dup["name"] == "Frontend_Interview_Prep.pdf"

    persisted_path = Path(materials[0]["file_path"])
    assert persisted_path.exists()


def test_persistence_store_load_list_is_empty_for_missing_material_file(tmp_path):
    storage_root = tmp_path / "data"
    assistant = StudyAssistant(storage_root=storage_root)
    assert assistant.get_materials() == []


def test_embed_chunks_real_model_smoke_check():
    assistant = StudyAssistant()

    results = assistant.embed_chunks([
        {"text": "The mitochondria power the cell.", "page": 1, "source": "biology.pdf"},
    ])

    assert len(results) == 1
    assert results[0]["text"] == "The mitochondria power the cell."
    assert results[0]["page"] == 1
    assert results[0]["source"] == "biology.pdf"
    assert isinstance(results[0]["embedding"], list)
    assert len(results[0]["embedding"]) > 1
    assert all(isinstance(value, float) for value in results[0]["embedding"])


def test_build_faiss_index_and_search_return_metadata_and_top_k_results():
    assistant = StudyAssistant()

    def vector_for(text_index):
        arr = np.zeros(384, dtype="float32")
        arr[text_index % 384] = 1.0
        return arr.astype(float).tolist()

    embedded_chunks = [
        {
            "text": "Photosynthesis turns light energy into chemical energy.",
            "page": 1,
            "source": "bio.pdf",
            "embedding": vector_for(0),
        },
        {
            "text": "Mitochondria power cellular respiration.",
            "page": 2,
            "source": "bio.pdf",
            "embedding": vector_for(1),
        },
    ]

    payload = assistant.build_faiss_index(embedded_chunks)
    index = payload["index"]
    metadata = payload["metadata"]

    assert index is not None
    assert index.ntotal == 2
    assert index.d == 384
    assert len(metadata) == 2
    assert [item["text"] for item in metadata] == [
        "Photosynthesis turns light energy into chemical energy.",
        "Mitochondria power cellular respiration.",
    ]

    query = vector_for(0)
    results = assistant.search_faiss(query, index, metadata, k=1)

    assert len(results) == 1
    assert results[0]["text"] == "Photosynthesis turns light energy into chemical energy."
    assert results[0]["page"] == 1
    assert results[0]["source"] == "bio.pdf"
    assert "similarity" in results[0]


def test_generate_answer_returns_mocked_grounded_answer_and_includes_requested_context(monkeypatch):
    assistant = StudyAssistant()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    from types import SimpleNamespace

    captured = {}

    class FakeModels:
        def generate_content(self, model, contents):
            captured["model"] = model
            captured["contents"] = contents
            assert "What is photosynthesis?" in contents
            assert "Photosynthesis turns light energy into chemical energy." in contents
            assert "general knowledge" in contents.lower()
            assert "I couldn't find this information in the study material." in contents
            assert "study material is the only source of truth" in contents.lower()
            return SimpleNamespace(text="Photosynthesis turns light energy into chemical energy.")

    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = FakeModels()

    try:
        from google import genai
    except Exception:
        genai = None

    if genai is not None:
        monkeypatch.setattr(genai, "Client", FakeClient)

    answer = assistant.generate_answer(
        "What is photosynthesis?",
        [
            {"text": "Photosynthesis turns light energy into chemical energy.", "page": 1, "source": "bio.pdf"},
        ],
    )

    assert answer == "Photosynthesis turns light energy into chemical energy."
    assert captured["model"] == "gemini-3.8-flash"
    assert "What is photosynthesis?" in captured["contents"]
    assert "Photosynthesis turns light energy into chemical energy." in captured["contents"]


def test_generate_answer_returns_fallback_for_empty_or_invalid_retrieval(monkeypatch):
    assistant = StudyAssistant()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class FailClient:
        def __init__(self, api_key):
            raise AssertionError("Gemini client should not be called when retrieval is empty")

    try:
        from google import genai
    except Exception:
        genai = None

    if genai is not None:
        monkeypatch.setattr(genai, "Client", FailClient)

    fallback = "I couldn't find this information in the study material."
    assert assistant.generate_answer("What is photosynthesis?", []) == fallback
    assert assistant.generate_answer("What is photosynthesis?", [{"text": "   ", "page": 1, "source": "bio.pdf"}]) == fallback


def test_generate_answer_returns_provider_message_when_gemini_request_fails(monkeypatch):
    assistant = StudyAssistant()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class FakeModels:
        def generate_content(self, model, contents):
            raise RuntimeError("503 UNAVAILABLE")

    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = FakeModels()

    try:
        from google import genai
    except Exception:
        genai = None

    if genai is not None:
        monkeypatch.setattr(genai, "Client", FakeClient)

    provider_message = "Gemini is temporarily unavailable. Please try again."
    assert assistant.generate_answer(
        "What is photosynthesis?",
        [{"text": "Photosynthesis turns light energy into chemical energy.", "page": 1, "source": "bio.pdf"}],
    ) == provider_message


def test_generate_answer_requires_gemini_api_key(monkeypatch):
    assistant = StudyAssistant()
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        assistant.generate_answer("What is photosynthesis?", [{"text": "Photosynthesis turns light energy into chemical energy.", "page": 1, "source": "bio.pdf"}])


def test_faiss_helpers_handle_empty_and_invalid_inputs_safely():
    assistant = StudyAssistant()

    assert assistant.build_faiss_index([]) == {"index": None, "metadata": []}
    assert assistant.build_faiss_index([
        {"text": "   ", "page": 1, "source": "bio.pdf", "embedding": []},
    ]) == {"index": None, "metadata": []}

    empty_index_payload = assistant.build_faiss_index([
        {"text": "Missing embeddings safely", "page": 1, "source": "bio.pdf", "embedding": None},
    ])
    assert empty_index_payload == {"index": None, "metadata": []}

    query = [1.0, 2.0, 3.0]
    assert assistant.search_faiss(query, None, [], k=3) == []
    assert assistant.search_faiss([], None, [], k=3) == []
