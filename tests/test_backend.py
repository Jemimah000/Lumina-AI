from services.study_assistant import StudyAssistant


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
