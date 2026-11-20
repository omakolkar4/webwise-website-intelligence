
import streamlit as st
from datetime import datetime
from urllib.parse import urlparse

from src.website_qa.rag_pipeline import (
    build_knowledge_base,
    answer_question
)


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Webwise | Website Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULTS = {
    "knowledge_base": [],
    "successful_urls": [],
    "failed_urls": [],
    "chat_history": [],
    "navigation": "Dashboard",
    "url_input": (
        "https://docs.python.org/3/\n"
        "https://docs.streamlit.io/\n"
        "https://developer.mozilla.org/en-US/docs/Web\n"
        "https://en.wikipedia.org/wiki/Artificial_intelligence\n"
        "https://www.nasa.gov/\n"
        "https://www.who.int/\n"
        "https://docs.github.com/en\n"
        "https://docs.scrapy.org/en/latest/\n"
        "https://developer.mozilla.org/en-US/docs/Web/HTML"
    ),
    "flash_message": "",
    "last_processed": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================================
# CALLBACK FUNCTIONS
# ==========================================================

# IMPORTANT:
# Navigation changes must happen through callbacks.
# Never directly modify the navigation key after
# the sidebar radio widget has been created.

def navigate_to(page):
    st.session_state.navigation = page


def clear_conversation():
    st.session_state.chat_history = []


def clear_url_list():
    st.session_state.url_input = ""


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* GLOBAL */

.stApp {
    background: var(--background-color);
    color: var(--text-color);
}

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont,
                 "Segoe UI", sans-serif;
}

.main .block-container {
    max-width: 1450px;
    padding: 2rem 2.5rem 3rem;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #111d38;
    border-right: 1px solid #263756;
}

[data-testid="stSidebar"] * {
    color: #edf3ff;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #c3d0e7;
}

.sidebar-brand {
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -1.2px;
    color: #ffffff;
}

.sidebar-tagline {
    font-size: 10px;
    letter-spacing: 1.5px;
    color: #93b5ed;
    margin-top: 5px;
}

.sidebar-section {
    color: #8da6cc;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
    margin-top: 22px;
    margin-bottom: 10px;
}

.sidebar-info {
    background: #1c2b49;
    border: 1px solid #304363;
    padding: 13px;
    border-radius: 11px;
    margin-top: 9px;
}

.sidebar-info-title {
    font-size: 12px;
    color: #9fb4d5;
}

.sidebar-info-value {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 5px;
}

/* HEADER */

.top-title {
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -1px;
    color: var(--text-color);
}

.top-subtitle {
    font-size: 13px;
    color: var(--text-color);
    opacity: 0.65;
    margin-top: 4px;
}

/* HERO */

.hero-card {
    background: linear-gradient(
        115deg,
        #182d59 0%,
        #354fa1 55%,
        #536bd1 100%
    );
    padding: 30px;
    border-radius: 18px;
    color: #ffffff;
    margin: 12px 0 25px;
    box-shadow: 0 10px 30px rgba(38, 65, 140, 0.16);
}

.hero-card h1 {
    color: #ffffff;
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -0.8px;
    margin-bottom: 8px;
}

.hero-card p {
    color: #e0e9ff;
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 0;
}

.hero-label {
    color: #c2d4ff;
    font-size: 10px;
    letter-spacing: 1.6px;
    font-weight: 700;
    margin-bottom: 12px;
}

/* METRIC CARDS */

.metric-card {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 15px;
    padding: 19px;
    min-height: 120px;
    transition: transform 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
}

.metric-icon {
    font-size: 21px;
    margin-bottom: 10px;
}

.metric-label {
    color: var(--text-color);
    opacity: 0.65;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
}

.metric-value {
    color: var(--text-color);
    font-size: 29px;
    font-weight: 800;
    margin-top: 6px;
}

/* SECTION HEADINGS */

.section-title {
    font-size: 19px;
    font-weight: 750;
    color: var(--text-color);
    margin-bottom: 5px;
}

.section-subtitle {
    font-size: 13px;
    color: var(--text-color);
    opacity: 0.65;
    margin-bottom: 18px;
}

/* CONTENT PANELS */

.content-panel {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 15px;
    padding: 19px;
    margin-bottom: 13px;
}

.panel-title {
    font-size: 15px;
    font-weight: 750;
    color: var(--text-color);
    margin-bottom: 6px;
}

.panel-description {
    color: var(--text-color);
    opacity: 0.65;
    font-size: 12px;
    line-height: 1.6;
}

/* WEBSITE CARDS */

.website-card {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
    transition: border 0.2s ease, transform 0.2s ease;
}

.website-card:hover {
    border-color: #657fe1;
    transform: translateY(-2px);
}

.website-name {
    color: var(--text-color);
    font-size: 13px;
    font-weight: 700;
    overflow-wrap: anywhere;
}

.website-url {
    color: var(--text-color);
    opacity: 0.65;
    font-size: 11px;
    margin-top: 6px;
    overflow-wrap: anywhere;
}

.website-url a {
    color: #6688ed;
    text-decoration: none;
}

.website-url a:hover {
    text-decoration: underline;
}

/* BUTTONS */

div.stButton > button {
    border-radius: 10px;
    min-height: 43px;
    font-weight: 650;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
}

/* INPUTS AND CHAT */

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    border-radius: 10px;
}

[data-testid="stChatMessage"] {
    border: 1px solid var(--border-color);
    border-radius: 13px;
    padding: 12px;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border-color);
    border-radius: 11px;
}

/* FOOTER */

.footer {
    text-align: center;
    color: var(--text-color);
    opacity: 0.55;
    font-size: 11px;
    padding: 18px 0 5px;
}

/* RESPONSIVE */

@media(max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }

    .hero-card {
        padding: 22px;
    }

    .hero-card h1 {
        font-size: 23px;
    }

    .top-title {
        font-size: 24px;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def show_header(title, description):
    st.markdown(
        f"""
        <div style="margin-bottom:22px;">
            <div class="top-title">{title}</div>
            <div class="top-subtitle">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_metrics():

    metrics = [
        ("🌐", "WEBSITE SOURCES",
         len(st.session_state.successful_urls)),

        ("📚", "CONTENT CHUNKS",
         len(st.session_state.knowledge_base)),

        ("💬", "QUESTIONS ASKED",
         len(st.session_state.chat_history))
    ]

    columns = st.columns(3)

    for column, (icon, label, value) in zip(columns, metrics):

        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def show_website_cards(websites):

    for item in websites:

        url = item["url"]

        st.markdown(
            f"""
            <div class="website-card">
                <div class="website-name">
                    🌐 {item["title"]}
                </div>
                <div class="website-url">
                    <a href="{url}" target="_blank">{url}</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def process_websites():

    urls = list(dict.fromkeys(
        line.strip()
        for line in st.session_state.url_input.splitlines()
        if line.strip()
    ))

    if not urls:
        st.warning("Please enter at least one website URL.")
        return

    if len(urls) > 10:
        st.warning("You can process up to 10 websites at a time.")
        return

    invalid_urls = []

    for url in urls:

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            invalid_urls.append(url)

    if invalid_urls:
        st.warning(
            "Please enter valid HTTP or HTTPS website URLs."
        )
        return

    progress = st.progress(0)
    status = st.empty()

    try:

        knowledge_base, successful, failed = build_knowledge_base(
            urls,
            progress_callback=lambda value, message: (
                progress.progress(value),
                status.info(message)
            )
        )

        st.session_state.knowledge_base = knowledge_base
        st.session_state.successful_urls = successful
        st.session_state.failed_urls = failed
        st.session_state.chat_history = []

        st.session_state.last_processed = datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )

        st.session_state.flash_message = (
            f"{len(successful)} website(s) processed successfully."
        )

        if failed:
            st.session_state.flash_message += (
                f" {len(failed)} website(s) could not be loaded."
            )

        st.rerun()

    except Exception as error:
        st.error(f"Website processing failed: {error}")


# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="padding:12px 0 22px;">
            <div class="sidebar-brand">🌐 Webwise</div>
            <div class="sidebar-tagline">
                WEBSITE INTELLIGENCE PLATFORM
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">MAIN MENU</div>',
        unsafe_allow_html=True
    )

    # The navigation key is initialized before this widget.
    # All navigation changes happen through on_click callbacks.

    st.radio(
        "Navigation",
        [
            "Dashboard",
            "AI Assistant",
            "Website Sources",
            "Analytics"
        ],
        key="navigation",
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-section">AI INFRASTRUCTURE</div>',
        unsafe_allow_html=True
    )

    knowledge_status = (
        "Ready"
        if st.session_state.knowledge_base
        else "Not connected"
    )

    st.markdown(
        f"""
        <div class="sidebar-info">
            <div class="sidebar-info-title">
                ● Local AI Engine
            </div>
            <div class="sidebar-info-value">
                Qwen 2.5 · 3B
            </div>
        </div>

        <div class="sidebar-info">
            <div class="sidebar-info-title">
                ● Embedding Engine
            </div>
            <div class="sidebar-info-value">
                Nomic Embed Text
            </div>
        </div>

        <div class="sidebar-info">
            <div class="sidebar-info-title">
                ● Knowledge Base
            </div>
            <div class="sidebar-info-value">
                {knowledge_status}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-section">WORKSPACE OVERVIEW</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"🌐 {len(st.session_state.successful_urls)} connected websites"
    )

    st.caption(
        f"📚 {len(st.session_state.knowledge_base)} content chunks"
    )

    st.caption(
        f"💬 {len(st.session_state.chat_history)} questions asked"
    )

    st.divider()

    st.markdown(
        """
        <div style="color:#8da6cc;font-size:11px;line-height:1.8;">
            WEBWISE v1.0<br>
            Powered by local AI<br>
            © Webwise
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# FLASH MESSAGE
# ==========================================================

if st.session_state.flash_message:

    st.success(st.session_state.flash_message)
    st.session_state.flash_message = ""


# ==========================================================
# DASHBOARD
# ==========================================================

if st.session_state.navigation == "Dashboard":

    show_header(
        "Dashboard",
        "Your central workspace for website intelligence."
    )

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-label">
                YOUR AI-POWERED WORKSPACE
            </div>
            <h1>Discover more. Search smarter.</h1>
            <p>
                Connect your favourite websites, explore their content
                and get intelligent answers using your own AI workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    show_metrics()

    st.write("")

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown(
            '<div class="section-title">🌐 Connected Websites</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Your active website knowledge sources.'
            '</div>',
            unsafe_allow_html=True
        )

        if st.session_state.successful_urls:

            show_website_cards(
                st.session_state.successful_urls[:5]
            )

            if len(st.session_state.successful_urls) > 5:
                st.caption(
                    f"+ {len(st.session_state.successful_urls) - 5} "
                    "more connected websites"
                )

        else:
            st.info(
                "No websites connected yet. Visit Website Sources to begin."
            )

        # FIXED: Use callback instead of directly changing navigation.
        st.button(
            "Manage Website Sources →",
            use_container_width=True,
            on_click=navigate_to,
            args=("Website Sources",)
        )

    with right:

        st.markdown(
            '<div class="section-title">⚡ Quick Actions</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Jump into your workspace.'
            '</div>',
            unsafe_allow_html=True
        )

        # FIXED BUTTON 1
        st.button(
            "💬 Open AI Assistant",
            use_container_width=True,
            on_click=navigate_to,
            args=("AI Assistant",)
        )

        # FIXED BUTTON 2
        st.button(
            "🌐 Add New Websites",
            use_container_width=True,
            on_click=navigate_to,
            args=("Website Sources",)
        )

        # FIXED BUTTON 3
        st.button(
            "📊 View Analytics",
            use_container_width=True,
            on_click=navigate_to,
            args=("Analytics",)
        )

        st.write("")

        st.markdown(
            """
            <div class="content-panel">
                <div class="panel-title">
                    ✨ Local AI Technology
                </div>
                <div class="panel-description">
                    Qwen 2.5 generates answers while Nomic Embed Text
                    powers semantic search. Processing runs through
                    your local Ollama service.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        '<div class="section-title">🕒 Recent Activity</div>',
        unsafe_allow_html=True
    )

    if st.session_state.chat_history:

        for chat in reversed(st.session_state.chat_history[-5:]):

            with st.expander(chat["question"]):
                st.write(chat["answer"])
                st.caption(
                    f"{len(chat['sources'])} source reference(s)"
                )

    elif st.session_state.last_processed:

        st.info(
            f"Last website processing: "
            f"{st.session_state.last_processed}"
        )

    else:

        st.caption(
            "Your recent website and question activity will appear here."
        )


# ==========================================================
# AI ASSISTANT
# ==========================================================

elif st.session_state.navigation == "AI Assistant":

    show_header(
        "AI Assistant",
        "Ask questions and discover information across your websites."
    )

    show_metrics()

    st.write("")

    if not st.session_state.knowledge_base:

        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-label">AI ASSISTANT</div>
                <h1>Your intelligent research companion.</h1>
                <p>
                    Connect website sources to start asking questions
                    and receive answers with source references.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # FIXED: Callback-based navigation.
        st.button(
            "Connect Websites →",
            type="primary",
            on_click=navigate_to,
            args=("Website Sources",)
        )

    else:

        st.markdown(
            '<div class="section-title">Conversation</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Answers are generated from your connected website content.'
            '</div>',
            unsafe_allow_html=True
        )

        # Display conversation history.

        for chat in st.session_state.chat_history:

            with st.chat_message("user"):
                st.write(chat["question"])

            with st.chat_message("assistant", avatar="🌐"):

                st.markdown(chat["answer"])

                with st.expander("🔗 Source references"):

                    for source in chat["sources"]:
                        st.markdown(f"- [{source}]({source})")

                if chat.get("retrieved"):

                    with st.expander("View retrieved website content"):

                        for item in chat["retrieved"]:

                            st.markdown(
                                f"**{item['title']}** "
                                f"· Relevance: {item['score']:.3f}"
                            )

                            st.write(item["text"])
                            st.caption(item["source"])
                            st.divider()

        question = st.chat_input(
            "Ask anything about your connected websites..."
        )

        if question:

            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant", avatar="🌐"):

                with st.spinner(
                    "Searching your websites and generating an answer..."
                ):

                    try:

                        answer, sources, results = answer_question(
                            question,
                            st.session_state.knowledge_base
                        )

                        if not sources:
                            sources = list(dict.fromkeys(
                                item["source"]
                                for score, item in results
                            ))

                        retrieved_content = []

                        for score, item in results:

                            retrieved_content.append({
                                "title": item["title"],
                                "text": item["text"],
                                "source": item["source"],
                                "score": float(score)
                            })

                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": answer,
                            "sources": sources,
                            "retrieved": retrieved_content
                        })

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Unable to generate answer: {error}"
                        )

        if st.session_state.chat_history:

            st.divider()

            st.button(
                "🗑️ Clear Conversation",
                on_click=clear_conversation
            )


# ==========================================================
# WEBSITE SOURCES
# ==========================================================

elif st.session_state.navigation == "Website Sources":

    show_header(
        "Website Sources",
        "Manage your connected websites and searchable content."
    )

    show_metrics()

    st.write("")

    left, right = st.columns([1.2, 0.8], gap="large")

    with left:

        st.markdown(
            '<div class="section-title">🌐 Add Website Sources</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Connect up to 10 websites to your knowledge base.'
            '</div>',
            unsafe_allow_html=True
        )

        st.text_area(
            "Website URLs",
            key="url_input",
            height=250,
            placeholder=(
                "https://docs.python.org/3/\n"
                "https://docs.streamlit.io/\n"
                "https://www.nasa.gov/"
            )
        )

        if st.button(
            "⚡ Process Websites",
            type="primary",
            use_container_width=True
        ):
            process_websites()

        st.button(
            "Clear Website List",
            on_click=clear_url_list,
            use_container_width=True
        )

    with right:

        st.markdown(
            '<div class="section-title">Processing Information</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="content-panel">
                <div class="panel-title">01 · Website Extraction</div>
                <div class="panel-description">
                    Retrieves readable content from website URLs.
                </div>
            </div>

            <div class="content-panel">
                <div class="panel-title">02 · Text Processing</div>
                <div class="panel-description">
                    Cleans and divides website content into chunks.
                </div>
            </div>

            <div class="content-panel">
                <div class="panel-title">03 · Embedding Generation</div>
                <div class="panel-description">
                    Generates vector embeddings using Ollama.
                </div>
            </div>

            <div class="content-panel">
                <div class="panel-title">04 · AI Retrieval</div>
                <div class="panel-description">
                    Retrieves relevant information for AI answers.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        '<div class="section-title">Connected Websites</div>',
        unsafe_allow_html=True
    )

    if st.session_state.successful_urls:

        show_website_cards(
            st.session_state.successful_urls
        )

    else:

        st.info("Your connected websites will appear here.")

    if st.session_state.failed_urls:

        st.warning(
            f"{len(st.session_state.failed_urls)} website(s) "
            "could not be processed."
        )

        for item in st.session_state.failed_urls:

            with st.expander(item["url"]):
                st.error(item["error"])


# ==========================================================
# ANALYTICS
# ==========================================================

elif st.session_state.navigation == "Analytics":

    show_header(
        "Analytics",
        "An overview of your website knowledge base and AI activity."
    )

    show_metrics()

    st.write("")

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="section-title">Website Overview</div>',
            unsafe_allow_html=True
        )

        if st.session_state.successful_urls:

            for item in st.session_state.successful_urls:

                st.markdown(
                    f"""
                    <div class="website-card">
                        <div class="website-name">
                            🌐 {item["title"]}
                        </div>
                        <div class="website-url">
                            {item["url"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.info("No website data available.")

    with right:

        st.markdown(
            '<div class="section-title">AI Activity</div>',
            unsafe_allow_html=True
        )

        if st.session_state.chat_history:

            for index, chat in enumerate(
                reversed(st.session_state.chat_history[-10:]),
                start=1
            ):

                with st.expander(
                    f"Question {index}: {chat['question']}"
                ):

                    st.write(chat["answer"])

                    st.caption(
                        f"Sources: {len(chat['sources'])}"
                    )

        else:

            st.info(
                "Your AI question activity will appear here."
            )

    st.divider()

    st.markdown(
        '<div class="section-title">Technology Configuration</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="content-panel">
                <div class="panel-title">AI Model</div>
                <div class="panel-description">
                    Qwen 2.5 · 3B
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="content-panel">
                <div class="panel-title">Embedding Model</div>
                <div class="panel-description">
                    Nomic Embed Text
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div class="content-panel">
                <div class="panel-title">AI Infrastructure</div>
                <div class="panel-description">
                    Local Ollama
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        🌐 Webwise · Website Intelligence Platform
        <br>
        Intelligent website search powered by local AI
    </div>
    """,
    unsafe_allow_html=True
)
