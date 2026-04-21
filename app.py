import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 1.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    /* Using clamp with a slightly more aggressive scale for impact */
    font-size: clamp(3rem, 8vw, 5.5rem); 
    font-weight: 800;
    line-height: 0.95; /* Tighter line height for the "Syne" font's bold profile */
    letter-spacing: -0.04em;
    
    /* Premium Gradient Effect */
    background: linear-gradient(180deg, #f0ebe0 0%, #d1ccc0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    
    /* Subtle depth to prevent it from looking flat against the dark background */
    text-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    
    margin: 0 0 1.5rem;
    padding-bottom: 0.1em; /* Prevents descenders from being cut off by the clip */
}

/* Optional: Add a subtle entrance animation */
.hero h1 {
    animation: heroFadeIn 1s ease-out forwards;
}

@keyframes heroFadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.hero h1 span {
    color: #ff8c32;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #a09890;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Horizontal Pipeline ── */
.horizontal-pipeline {
    display: flex;
    gap: 1rem;
    justify-content: space-between;
    margin-bottom: 2rem;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 2rem 0;
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
    opacity: 0.95 !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}
/* Disabled styling */
.stButton > button:disabled {
    background: #302d2a !important;
    color: #605850 !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
    flex: 1;
}
.step-card.active {
    border-color: rgba(255,140,50,0.4);
    background: rgba(255,140,50,0.04);
}
.step-card.done {
    border-color: rgba(80,200,120,0.3);
    background: rgba(80,200,120,0.03);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.05);
    transition: background 0.3s;
}
.step-card.active::before { background: #ff8c32; }
.step-card.done::before   { background: #50c878; }

.step-header {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #ff8c32;
    opacity: 0.7;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #f0ebe0;
}
.step-status {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    margin-top: 0.2rem;
}
.status-waiting  { color: #555; }
.status-running  { color: #ff8c32; }
.status-done     { color: #50c878; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #cdc8bf;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(80,200,120,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.orange {
    color: #ff8c32;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.panel-label.green {
    color: #50c878;
    border-bottom: 1px solid rgba(80,200,120,0.15);
}

.stSpinner > div { color: #ff8c32 !important; }

details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #a09890 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0ebe0;
    margin: 2rem 0 1rem;
}

.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #605850;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a horizontal step card ─────────────────────────────────────
def step_card(num: str, title: str, state: str):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate to deliver a polished research report.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Dynamic Pipeline Calculation ──
r = st.session_state.results
def get_step_state(step_key):
    steps_order = ["search", "reader", "writer", "critic"]
    if step_key in r:
        return "done"
    if st.session_state.running:
        # Check if this is the first incomplete step
        for k in steps_order:
            if k not in r:
                return "running" if k == step_key else "waiting"
    return "waiting"

# ── Horizontal Pipeline Display ──
col_p1, col_p2, col_p3, col_p4 = st.columns(4)
with col_p1:
    step_card("01", "Search Agent", get_step_state("search"))
with col_p2:
    step_card("02", "Reader Agent", get_step_state("reader"))
with col_p3:
    step_card("03", "Writer Chain", get_step_state("writer"))
with col_p4:
    step_card("04", "Critic Chain", get_step_state("critic"))

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Input Area ──
topic = st.text_input(
    "Research Topic",
    placeholder="e.g. Quantum computing breakthroughs in 2025",
    key="topic_input",
)
# Button is disabled if pipeline is currently running
run_btn = st.button(
    "⚡  Run Research Pipeline", 
    use_container_width=True, 
    disabled=st.session_state.running
)


# ── Run pipeline Logic ────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    if "search" not in st.session_state.results:
        with st.spinner("🔍  Search Agent is working…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            st.session_state.results["search"] = sr["messages"][-1].content
            st.rerun() 

    # ── Step 2: Reader ──
    if "reader" not in st.session_state.results:
        with st.spinner("📄  Reader Agent is scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', pick relevant info:\n\n"
                    f"{st.session_state.results['search'][:800]}"
                )]
            })
            st.session_state.results["reader"] = rr["messages"][-1].content
            st.rerun() 

    # ── Step 3: Writer ──
    if "writer" not in st.session_state.results:
        with st.spinner("✍️  Writer is drafting the report…"):
            research_combined = f"SEARCH:\n{st.session_state.results['search']}\n\nREAD:\n{st.session_state.results['reader']}"
            st.session_state.results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.rerun() 

    # ── Step 4: Critic ──
    if "critic" not in st.session_state.results:
        with st.spinner("🧐  Critic is reviewing the report…"):
            st.session_state.results["critic"] = critic_chain.invoke({
                "report": st.session_state.results["writer"]
            })
            st.session_state.running = False
            st.session_state.done = True
            st.rerun() 

# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown("""<div class="report-panel"><div class="panel-label orange">📝 Final Research Report</div>""", unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Download Report Button
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("""<div class="feedback-panel"><div class="panel-label green">🧐 Critic Feedback</div>""", unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""<div class="notice">ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit</div>""", unsafe_allow_html=True)