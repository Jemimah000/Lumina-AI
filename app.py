import streamlit as st

from services.study_assistant import StudyAssistant

st.set_page_config(
    page_title="Lumina AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

with open("assets/style.css", encoding="utf-8") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

PAGE_LABELS = ["Dashboard", "Materials", "History", "Saved", "Upload", "Ask AI"]


def get_assistant() -> StudyAssistant:
    if "assistant" not in st.session_state:
        st.session_state["assistant"] = StudyAssistant()
    return st.session_state["assistant"]


def normalize_page(raw_page: str) -> str:
    if raw_page in PAGE_LABELS:
        return raw_page
    return "Dashboard"


def get_route_page() -> str:
    raw_page = st.query_params.get("page", "Dashboard")
    if isinstance(raw_page, list):
        raw_page = raw_page[0] if raw_page else "Dashboard"
    return normalize_page(str(raw_page))


def nav_link(label: str, active_page: str) -> str:
    state = "active" if label == active_page else ""
    return f'<a class="nav-item {state}" href="?page={label}">{label}</a>'


def ensure_assistant() -> StudyAssistant:
    if "assistant" not in st.session_state:
        st.session_state["assistant"] = StudyAssistant()
    return st.session_state["assistant"]


def extract_material_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    file_data = uploaded_file.getvalue()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return StudyAssistant.extract_pdf_text(file_data)
    if name.endswith((".txt", ".md")):
        return file_data.decode("utf-8", errors="ignore")
    return file_data.decode("utf-8", errors="ignore")


def render_top_nav(active_page: str) -> None:
    nav_items = "".join(
        nav_link(label, active_page)
        for label in ["Dashboard", "Materials", "History", "Saved"]
    )
    top_html = f"""
    <div class="topbar">
        <div class="brand">Lumina AI</div>
        <div class="nav-items">{nav_items}</div>
        <div class="top-actions">
            <a class="action-link" href="?page=Upload">Upload</a>
            <a class="action-pill" href="?page=Ask AI">Ask AI</a>
        </div>
    </div>
    """
    st.markdown(top_html, unsafe_allow_html=True)


def render_dashboard() -> None:
    assistant = get_assistant()
    materials_count = len(assistant.get_materials())
    history_count = len(assistant.get_history())
    saved_count = len(assistant.get_saved_answers())

    left_col, right_col = st.columns([1.2, 1], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="eyebrow">YOUR EMPATHETIC STUDY PARTNER</div>
            <div class="hero-title">Study Smarter.<br><span>Understand Faster.</span></div>
            <p class="hero-copy">
                Ask questions directly from your study materials and get clear,
                supportive answers grounded entirely in your own notes.
                No hallucinations. Just focus.
            </p>
            <div class="hero-links">
                <a class="btn-primary" href="?page=Ask AI">Ask Your Notes</a>
                <a class="btn-ghost" href="?page=Upload">Upload Materials</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            """
            <div class="hero-visual-wrap">
                <div class="upload-chip">Biology_Midterm.pdf<br><small>Uploaded 2 mins ago</small></div>
                <div class="hero-visual">🐧</div>
                <div class="answer-card">
                    <strong>AI Explanation</strong>
                    <p>Mitochondria generate most of the cell's energy by producing ATP.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="focus-wrap">
            <h2>Focus on what matters.</h2>
            <p>We designed Lumina to clear the noise and help you dive straight into learning.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-dot">◌</div>
                <h3>Your Materials</h3>
                <p>{materials_count} file(s) ready for study questions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-dot">◍</div>
                <h3>Smart Answers</h3>
                <p>{history_count} question(s) already answered in your workspace.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-dot">◎</div>
                <h3>Source Based</h3>
                <p>{saved_count} saved answer(s) ready for quick revision.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_materials() -> None:
    assistant = get_assistant()
    st.markdown('<div class="page-title">Materials</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Browse all uploaded notes and organize study packs by course.</p>',
        unsafe_allow_html=True,
    )

    materials = assistant.get_materials()
    if not materials:
        st.info("No materials yet. Go to Upload to add your first file.")
        return

    for material in materials:
        with st.container():
            st.markdown(f"### {material['name']}")
            st.caption(f"Source: {material['source_type']} • Uploaded {material['uploaded_at']}")
            st.write(material["content"][:500] + ("..." if len(material["content"]) > 500 else ""))
            st.markdown("---")


def render_history() -> None:
    assistant = get_assistant()
    st.markdown('<div class="page-title">History</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Revisit recent questions and continue from where you paused.</p>',
        unsafe_allow_html=True,
    )

    history = assistant.get_history()
    if not history:
        st.info("Your recent AI conversations will appear here.")
        return

    for item in reversed(history):
        with st.container():
            st.markdown(f"**Q:** {item['question']}")
            st.write(item["answer"].get("answer", "No answer available."))
            st.caption(item["created_at"])
            st.markdown("---")


def render_saved() -> None:
    assistant = get_assistant()
    st.markdown('<div class="page-title">Saved</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Bookmark important explanations and keep them ready for revision.</p>',
        unsafe_allow_html=True,
    )

    saved_answers = assistant.get_saved_answers()
    if not saved_answers:
        st.info("You have not saved any answers yet.")
        return

    for item in reversed(saved_answers):
        st.markdown(f"### Saved explanation")
        st.write(item["answer"].get("answer", "No answer available."))
        st.caption(item["saved_at"])
        st.markdown("---")


def render_upload() -> None:
    assistant = get_assistant()
    st.markdown('<div class="page-title">Upload Materials</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Add PDFs, notes, and study documents to build your personal knowledge base.</p>',
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Choose your study files",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        loaded_materials = []
        for uploaded_file in uploaded_files:
            if uploaded_file is None:
                continue

            file_name = uploaded_file.name
            text_value = extract_material_text(uploaded_file)
            if not text_value.strip():
                text_value = "Uploaded study document: " + file_name

            assistant.add_material(file_name, text_value, source_type="upload")
            loaded_materials.append(file_name)

        if loaded_materials:
            st.success(f"Added {len(loaded_materials)} material(s) to your study library.")


def render_ask_ai() -> None:
    assistant = get_assistant()
    st.markdown('<div class="page-title">Ask AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Ask a question and receive a source-grounded explanation from your materials.</p>',
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "What would you like to understand today?",
        placeholder="Explain photosynthesis in simple steps",
        value=st.session_state.get("draft_question", ""),
    )
    st.session_state["draft_question"] = question

    if st.button("Generate Answer"):
        if not question.strip():
            st.warning("Please enter a question first.")
            return

        answer = assistant.answer_question(question)
        assistant.add_history(question, answer)

        st.markdown("### Answer")
        st.success(answer["answer"])

        if answer.get("key_points"):
            st.markdown("#### Key points")
            for point in answer["key_points"]:
                st.write(f"- {point.get('title', 'Key point')}: {point.get('detail', '')}")

        if answer.get("source_materials"):
            st.markdown("#### Source materials")
            for source in answer["source_materials"]:
                st.caption(f"{source.get('title', 'Source')} • {source.get('page', 'N/A')} • {source.get('time', '')}")

        if st.button("Save this answer"):
            assistant.save_answer(answer)
            st.success("Answer saved to Saved.")


current_page = get_route_page()
st.session_state["page"] = current_page

render_top_nav(current_page)

if current_page == "Dashboard":
    render_dashboard()
elif current_page == "Materials":
    render_materials()
elif current_page == "History":
    render_history()
elif current_page == "Saved":
    render_saved()
elif current_page == "Upload":
    render_upload()
elif current_page == "Ask AI":
    render_ask_ai()