import streamlit as st
from pathlib import Path

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
UPLOAD_DIR = Path("data/uploads")

if "assistant" not in st.session_state:
    st.session_state.assistant = StudyAssistant()
if "materials" not in st.session_state:
    st.session_state.materials = []


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
            """
            <div class="feature-card">
                <div class="feature-dot">◌</div>
                <h3>Your Materials</h3>
                <p>
                    Upload lecture slides, PDFs, and written notes.
                    Keep every study hub organized in one clean space.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-dot">◍</div>
                <h3>Smart Answers</h3>
                <p>
                    Ask naturally and get precise tutor-like responses
                    that break difficult ideas into clear steps.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-dot">◎</div>
                <h3>Source Based</h3>
                <p>
                    Every answer cites your own uploaded content,
                    so you can trust where each idea comes from.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_materials() -> None:
    st.markdown(
        """
        <div class="materials-shell">
          <aside class="materials-sidebar">
            <div class="sidebar-brand"><span class="brand-mark">✦</span><div><b>Lumina</b><small>Your Study Partner</small></div></div>
            <div class="sidebar-nav"><a>▦ &nbsp; Home</a><a class="selected">▣ &nbsp; My Library</a><a>▱ &nbsp; Chat History</a><a>♧ &nbsp; Bookmarks</a><a>⚙ &nbsp; Settings</a></div>
            <div class="sidebar-footer"><a>ⓘ &nbsp; Help</a><a>♙ &nbsp; Privacy</a></div>
          </aside>
          <section class="materials-main">
            <div class="materials-heading"><div><h1>My Study Materials 📚</h1><p>Manage your uploaded notes, textbooks, and resources. Let Lumina help you study smarter.</p></div><a class="icon-upload" href="?page=Upload">↥</a></div>
        """,
        unsafe_allow_html=True,
    )
    tab_col, search_col = st.columns([1.4, 1], gap="medium")
    with tab_col:
        selected_tab = st.radio("Material filter", ["All", "Recent", "Favorites"], horizontal=True, label_visibility="collapsed")
    with search_col:
        search_term = st.text_input("Search materials", placeholder="⌕  Search materials...", label_visibility="collapsed")

    materials = st.session_state.materials
    if search_term.strip():
        query = search_term.lower().strip()
        materials = [item for item in materials if query in item["name"].lower() or query in item["text"].lower()]
    if selected_tab == "Recent":
        materials = materials[-3:]
    elif selected_tab == "Favorites":
        materials = [item for item in materials if item.get("favorite")]

    st.markdown('<div class="material-grid">', unsafe_allow_html=True)
    if not materials:
        st.markdown('<div class="empty-materials">No materials yet. Upload your first note to generate short notes and similar words.</div>', unsafe_allow_html=True)
    for index, material in enumerate(materials):
        file_type = Path(material["name"]).suffix.replace(".", "").upper() or "NOTE"
        status = material.get("status", "Ready")
        st.markdown(
            f'''<div class="material-card"><div class="file-icon">▣</div><span class="status-badge">◉ {status}</span><h3>{material["name"]}</h3><p class="file-meta">▧ {file_type} &nbsp; ◷ {material.get("uploaded", "Just now")}</p><div class="card-actions"><form><button formaction="?page=Ask AI" class="ask-card-button">✦ Ask AI</button></form><span class="open-card">↗</span></div></div>''',
            unsafe_allow_html=True,
        )
        with st.expander(f"View notes: {material['name']}", expanded=False):
            st.markdown("**Short notes**")
            st.write(material["short_notes"])
            st.markdown("**Similar words**")
            st.write(", ".join(material["similar_words"]) or "No related terms found")
    st.markdown('</div></section></div>', unsafe_allow_html=True)


def render_history() -> None:
    st.markdown('<div class="page-title">History</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Revisit recent questions and continue from where you paused.</p>',
        unsafe_allow_html=True,
    )
    st.info("Your recent AI conversations will appear here.")


def render_saved() -> None:
    st.markdown('<div class="page-title">Saved</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Bookmark important explanations and keep them ready for revision.</p>',
        unsafe_allow_html=True,
    )
    st.info("You have not saved any answers yet.")


def render_upload() -> None:
    st.markdown('<div class="page-title">Upload PDF Notes</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Choose a PDF from your computer. Lumina will save it, create short notes, and find similar words.</p>',
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Select PDF files from your computer",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True,
        help="You can select one or more PDF files from your computer.",
    )
    if uploaded_files:
        st.caption(f"Selected {len(uploaded_files)} file(s): " + ", ".join(file.name for file in uploaded_files))
    if uploaded_files and st.button("Upload and create notes"):
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        for uploaded_file in uploaded_files:
            try:
                file_bytes = uploaded_file.getvalue()
                text = st.session_state.assistant.extract_text(uploaded_file.name, file_bytes)
                material = st.session_state.assistant.add_material(uploaded_file.name, text)
                material["uploaded"] = "Just now"
                material["status"] = "Ready"
                if not any(item["name"] == material["name"] for item in st.session_state.materials):
                    st.session_state.materials.append(material)
                (UPLOAD_DIR / uploaded_file.name).write_bytes(file_bytes)
                st.success(f"{uploaded_file.name} processed successfully.")
            except ValueError as error:
                st.error(f"{uploaded_file.name}: {error}")


def render_ask_ai() -> None:
    st.markdown('<div class="page-title">Ask AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Ask a question and receive a source-grounded explanation from your materials.</p>',
        unsafe_allow_html=True,
    )
    question = st.text_area("What would you like to understand today?", placeholder="Explain photosynthesis in simple steps")
    if st.button("Generate Answer"):
        if question.strip():
            result = st.session_state.assistant.answer_question(question)
            st.success(result["answer"])
            if result["key_points"]:
                for point in result["key_points"]:
                    st.markdown(f"**{point['title']}**: {point['detail']}")
            if result["source_materials"]:
                st.caption(f"Source: {result['source_materials'][0]['title']}")
        else:
            st.warning("Please enter a question first.")


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