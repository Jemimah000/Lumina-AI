import streamlit as st

st.set_page_config(
    page_title="Lumina AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("assets/style.css", encoding="utf-8") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def set_page(page_name: str) -> None:
    st.session_state["page"] = page_name


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">✦</div>
            <div>
                <div class="brand-name">Lumina AI</div>
                <div class="brand-tagline">Your Study Companion</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-space'></div>", unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True):
        st.session_state.clear()

    st.markdown("<div class='nav-space'></div>", unsafe_allow_html=True)

    if st.button("⌂  Home", use_container_width=True):
        set_page("Home")
    if st.button("▣  My Library", use_container_width=True):
        set_page("Library")
    if st.button("✦  Ask AI", use_container_width=True):
        set_page("Ask AI")
    if st.button("◷  History", use_container_width=True):
        set_page("History")
    if st.button("♡  Bookmarks", use_container_width=True):
        set_page("Bookmarks")
    if st.button("⚙  Settings", use_container_width=True):
        set_page("Settings")

    st.markdown("<div class='sidebar-bottom'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="profile">
            <div class="profile-avatar">V</div>
            <div>
                <div class="profile-name">Student</div>
                <div class="profile-role">Learner</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="welcome">
        <div class="eyebrow">YOUR AI STUDY COMPANION</div>
        <h1>Study smarter with <span>Lumina</span>.</h1>
        <p>
            Ask questions, explore your study materials,
            and get clear answers grounded in your notes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)