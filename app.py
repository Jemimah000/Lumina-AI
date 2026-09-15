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
MATERIALS_DIR = Path("data/materials")
MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

if "assistant" not in st.session_state:
    st.session_state.assistant = StudyAssistant()
assistant = st.session_state.assistant


def sync_streamlit_state_from_assistant() -> None:
    assistant = st.session_state.get("assistant")
    if assistant is None:
        return
    st.session_state.materials = assistant.get_materials()
    st.session_state.faiss_index = assistant.faiss_index
    st.session_state.faiss_metadata = getattr(assistant, "faiss_metadata", [])


if "materials" not in st.session_state:
    sync_streamlit_state_from_assistant()
if "faiss_index" not in st.session_state:
    sync_streamlit_state_from_assistant()
if "faiss_metadata" not in st.session_state:
    sync_streamlit_state_from_assistant()


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
    return f'<a class="nav-item {state}" href="?page={label}" target="_self">{label}</a>'


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
            <a class="action-link" href="?page=Upload" target="_self">Upload</a>
            <a class="action-pill" href="?page=Ask AI" target="_self">Ask AI</a>
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
                <a class="btn-primary" href="?page=Ask AI" target="_self">Ask Your Notes</a>
                <a class="btn-ghost" href="?page=Upload" target="_self">Upload Materials</a>
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
            <div class="materials-heading"><div><h1>My Study Materials 📚</h1><p>Manage your uploaded notes, textbooks, and resources. Let Lumina help you study smarter.</p></div><a class="icon-upload" href="?page=Upload" target="_self">↥</a></div>
        """,
        unsafe_allow_html=True,
    )

    # Close the structural HTML shell before rendering the Streamlit widgets.
    # This avoids nesting streamlit widgets inside the raw HTML section shell.
    st.markdown("</section></div>", unsafe_allow_html=True)

    tab_col, search_col = st.columns([1.4, 1], gap="medium")
    with tab_col:
        selected_tab = st.radio("Material filter", ["All", "Recent", "Favorites"], horizontal=True, label_visibility="collapsed")
    with search_col:
        search_term = st.text_input("Search materials", placeholder="⌕  Search materials...", label_visibility="collapsed")

    sync_streamlit_state_from_assistant()
    assistant = st.session_state.assistant
    materials = assistant.get_materials()
    if search_term.strip():
        query = search_term.lower().strip()
        materials = [
            item for item in materials
            if query in item["name"].lower()
            or query in (item.get("text") or item.get("content") or "").lower()
        ]
    if selected_tab == "Recent":
        materials = materials[-3:]
    elif selected_tab == "Favorites":
        materials = [item for item in materials if item.get("favorite")]

    st.markdown('<div class="material-grid">', unsafe_allow_html=True)
    if not materials:
        st.markdown('<div class="empty-materials">No materials yet. Upload your first note to generate short notes and similar words.</div>', unsafe_allow_html=True)
    for index, material in enumerate(materials):
        name = material.get("name") or "Untitled material"
        file_type = Path(name).suffix.replace(".", "").upper() or "PDF"
        status = material.get("status", "Ready")
        uploaded = material.get("uploaded", material.get("uploaded_at", "Just now"))
        st.markdown(
            f'''<div class="material-card"><div class="file-icon">▣</div><span class="status-badge">◉ {status}</span><h3>{name}</h3><p class="file-meta">▧ {file_type} &nbsp; ◷ {uploaded}</p><div class="card-actions"><form action="?page=Ask AI" method="get" target="_self"><button formaction="?page=Ask AI" class="ask-card-button">✦ Ask AI</button></form><span class="open-card">↗</span></div></div>''',
            unsafe_allow_html=True,
        )
        with st.expander(f"View notes: {name}", expanded=False):
            st.markdown("**Short notes**")
            st.write(material.get("short_notes", ""))
            st.markdown("**Similar words**")
            st.write(", ".join(material.get("similar_words") or []) or "No related terms found")
    st.markdown('</div>', unsafe_allow_html=True)


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
        MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
        assistant = st.session_state.assistant
        pdf_records = []
        errors = []

        for uploaded_file in uploaded_files:
            try:
                file_bytes = uploaded_file.getvalue()
                file_hash = StudyAssistant._material_file_hash(file_bytes)
                safe_name = StudyAssistant._safe_uploaded_name(uploaded_file.name)
                safe_path = MATERIALS_DIR / safe_name
                safe_path.write_bytes(file_bytes)

                text = assistant.extract_text(uploaded_file.name, file_bytes)
                material = assistant.add_material(
                    uploaded_file.name,
                    text,
                    file_path=str(safe_path),
                    file_hash=file_hash,
                    page_count=0,
                )

                material["uploaded"] = "Just now"
                material["status"] = "Ready"
                material["source"] = uploaded_file.name
                material["file_type"] = Path(uploaded_file.name).suffix.lower().lstrip(".") or "note"

                if uploaded_file.name.lower().endswith(".pdf"):
                    records = StudyAssistant.extract_pdf_page_records(file_bytes, uploaded_file.name)
                    pdf_records.extend(records)
                    material["page_count"] = len(records)
                    material["source"] = uploaded_file.name
                    material["file_type"] = "pdf"
                else:
                    material["page_count"] = 0

                assistant.materials[-1] = material
                st.session_state.assistant = assistant
                st.session_state.materials = assistant.get_materials()

            except Exception as error:
                errors.append(f"{uploaded_file.name}: {error}")
                st.error(f"{uploaded_file.name}: {error}")

        if errors:
            st.error("One or more files failed during the upload processing chain.")
            return

        # Build the uploaded PDF RAG state once and persist it on the
        # canonical session assistant object and explicitly on streamlit
        # session memory so Ask AI uses the same FAISS pair after reloads.
        if pdf_records:
            try:
                chunks = StudyAssistant.chunk_page_records(pdf_records)
                embedded = assistant.embed_chunks(chunks)
                rag = StudyAssistant.build_faiss_index(embedded)

                if rag.get("index") is None or not rag.get("metadata"):
                    raise ValueError("FAISS index or metadata is empty after PDF processing.")

                assistant.faiss_index = rag["index"]
                assistant.faiss_metadata = rag["metadata"]
                st.session_state.assistant = assistant
                st.session_state.faiss_index = rag["index"]
                st.session_state.faiss_metadata = rag["metadata"]

                st.success(f"{uploaded_file.name} processed successfully.")
                sync_streamlit_state_from_assistant()

            except Exception as error:
                st.error(f"FAISS build failed: {error}")
                assistant.faiss_index = None
                assistant.faiss_metadata = []
                st.session_state.assistant = assistant
                st.session_state.faiss_index = None
                st.session_state.faiss_metadata = []
                return
        else:
            assistant.faiss_index = None
            assistant.faiss_metadata = []
            st.session_state.assistant = assistant
            st.session_state.faiss_index = None
            st.session_state.faiss_metadata = []

        sync_streamlit_state_from_assistant()


def render_ask_ai() -> None:
    st.markdown('<div class="page-title">Ask AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Ask a question and receive a source-grounded explanation from your materials.</p>',
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "What would you like to understand today?",
        placeholder="Explain photosynthesis in simple steps",
    )

    if st.button("Generate Answer"):
        if question.strip():
            sync_streamlit_state_from_assistant()
            assistant = st.session_state.assistant
            index = st.session_state.get("faiss_index") or assistant.faiss_index
            metadata = st.session_state.get("faiss_metadata") or assistant.faiss_metadata or []

            # If the current session lost the FAISS vector state but the
            # material JSON and PDF bytes still exist on disk, rebuild the
            # RAG objects deterministically from those persisted sources.
            if index is None or not metadata:
                rag = assistant.rebuild_rag_from_persisted_materials()
                index = rag.get("index") if isinstance(rag, dict) else None
                metadata = rag.get("metadata") if isinstance(rag, dict) else []

            assistant.faiss_index = index
            assistant.faiss_metadata = metadata
            st.session_state.assistant = assistant
            st.session_state.faiss_index = index
            st.session_state.faiss_metadata = metadata

            if index is not None and metadata:
                try:
                    retrieved_chunks = assistant.retrieve_relevant_chunks(
                        question,
                        index,
                        metadata,
                        k=5,
                    )
                except Exception:
                    retrieved_chunks = []

                if retrieved_chunks:
                    answer = assistant.generate_answer(question, retrieved_chunks)
                    st.success(answer)
                    first = retrieved_chunks[0]
                    st.caption(f"Source: {first.get('source') or 'Uploaded material'} | Page {first.get('page') or 'unknown'}")
                    return

            # Exact fallback sentence when no RAG items are available.
            st.success("I couldn't find this information in the study material.")
            st.caption("Source: Uploaded material")
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