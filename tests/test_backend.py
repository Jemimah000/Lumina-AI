from services.study_assistant import StudyAssistant


class FakeEmbeddingModel:
    def embed_documents(self, texts):
        return [[4.0, 5.0, 6.0] for _ in texts]


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


def test_study_assistant_returns_structured_answer():
    assistant = StudyAssistant()
    result = assistant.answer_question("How does a hash table handle collisions?")

    assert "hash" in result["answer"].lower()
    assert isinstance(result["key_points"], list) and result["key_points"]
    assert isinstance(result["source_materials"], list)


def test_study_assistant_tracks_uploads_history_and_saved_answers():
    assistant = StudyAssistant()
    assistant.add_material("Biology Notes", "Photosynthesis converts sunlight into chemical energy.")

    answer = assistant.answer_question("What is photosynthesis?")

    assert "photosynthesis" in answer["answer"].lower()
    assert len(assistant.get_materials()) == 1

    assistant.add_history("What is photosynthesis?", answer)
    assistant.save_answer(answer)

    assert len(assistant.get_history()) == 1
    assert len(assistant.get_saved_answers()) == 1


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
