import streamlit as st

st.set_page_config(
    page_title="Lumina AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

with open("assets/style.css", encoding="utf-8") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

PAGE_LABELS = ["Dashboard", "Materials", "History", "Saved", "Upload", "Ask AI"]


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
    st.markdown('<div class="page-title">Materials</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Browse all uploaded notes and organize study packs by course.</p>',
        unsafe_allow_html=True,
    )
    st.info("No materials yet. Go to Upload to add your first file.")


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
    st.markdown('<div class="page-title">Upload Materials</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Add PDFs, notes, and study documents to build your personal knowledge base.</p>',
        unsafe_allow_html=True,
    )
    st.file_uploader("Choose your study files", type=["pdf", "txt", "md", "docx"], accept_multiple_files=True)


def render_ask_ai() -> None:
    st.markdown('<div class="page-title">Ask AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-copy">Ask a question and receive a source-grounded explanation from your materials.</p>',
        unsafe_allow_html=True,
    )
    question = st.text_area("What would you like to understand today?", placeholder="Explain photosynthesis in simple steps")
    if st.button("Generate Answer"):
        if question.strip():
            st.success("Your AI answer would appear here after backend integration.")
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