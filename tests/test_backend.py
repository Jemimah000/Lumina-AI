from services.study_assistant import StudyAssistant


def test_study_assistant_returns_structured_answer():
    assistant = StudyAssistant()
    result = assistant.answer_question("How does a hash table handle collisions?")

    assert "hash" in result["answer"].lower()
    assert isinstance(result["key_points"], list) and result["key_points"]
    assert isinstance(result["source_materials"], list)
