"""
PowerPilot AI — Streamlit Application Entry Point
Futuristic Energy Intelligence Dashboard
"""
import os
import sys
import streamlit as st

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PowerPilot AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Load CSS ─────────────────────────────────────────────────────────────────
def load_css():
    css_files = [
        os.path.join(os.path.dirname(__file__), "styles", "main.css"),
        os.path.join(os.path.dirname(__file__), "styles", "animation.css"),
    ]
    combined = ""
    for path in css_files:
        if os.path.exists(path):
            with open(path) as f:
                combined += f.read() + "\n"
    if combined:
        st.markdown(f"<style>{combined}</style>", unsafe_allow_html=True)

load_css()

# ─── Hide Streamlit's auto-generated multi-page sidebar nav ───────────────────
# Streamlit automatically lists files in /pages/ as navigation items — we hide
# those because we use our own custom radio navigation below.
st.markdown("""
<style>
  /* Hide auto-generated Streamlit page navigation */
  [data-testid="stSidebarNav"] { display: none !important; }

  /* Style our custom home button */
  div[data-testid="stSidebar"] .home-btn button {
    background: linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,212,255,0.1)) !important;
    border: 1px solid rgba(0,255,136,0.35) !important;
    color: #00ff88 !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 2px !important;
    width: 100% !important;
    margin-bottom: 16px !important;
  }
  div[data-testid="stSidebar"] .home-btn button:hover {
    border-color: #00ff88 !important;
    box-shadow: 0 0 20px rgba(0,255,136,0.4) !important;
    transform: translateY(-1px) !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── Session state for current page ───────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 30px;">
      <div style="font-family:'Orbitron',monospace; font-size:1.4rem; font-weight:800;
                  color:#00d4ff; text-shadow:0 0 20px rgba(0,212,255,0.6);
                  letter-spacing:3px;">⚡ PowerPilot</div>
      <div style="font-family:'Exo 2',sans-serif; font-size:0.65rem;
                  color:rgba(232,244,253,0.4); letter-spacing:4px;
                  margin-top:4px;">ENERGY INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

    # Status indicator
    st.markdown("""
    <div style="display:flex; align-items:center; margin: 0 0 20px 8px;">
      <div class="status-dot"></div>
      <span style="font-family:'Share Tech Mono',monospace; font-size:0.7rem;
                   color:rgba(0,255,136,0.8);">SYSTEM ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 🏠 Home Button ──────────────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="home-btn">', unsafe_allow_html=True)
        if st.button("🏠  HOME — DASHBOARD", use_container_width=True, key="home_btn"):
            st.session_state.current_page = "🏠 Dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Navigation Radio ────────────────────────────────────────────────────
    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "🔮 Predictions", "🚨 Anomalies", "📊 Analytics"],
        index=["🏠 Dashboard", "🔮 Predictions", "🚨 Anomalies", "📊 Analytics"].index(
            st.session_state.current_page
        ),
        label_visibility="collapsed",
        key="nav_radio",
    )
    # Keep session_state in sync with radio
    if page != st.session_state.current_page:
        st.session_state.current_page = page

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.6rem;
                color:rgba(232,244,253,0.25); text-align:center; padding:10px;">
      POWERPILOT AI v1.0<br/>
      © 2024 Energy Intelligence
    </div>
    """, unsafe_allow_html=True)

# ─── Page Routing ─────────────────────────────────────────────────────────────
active = st.session_state.current_page

if active == "🏠 Dashboard":
    from pages.dashboard import render
    render()
elif active == "🔮 Predictions":
    from pages.prediction import render
    render()
elif active == "🚨 Anomalies":
    from pages.anomaly import render
    render()
elif active == "📊 Analytics":
    from pages.analytics import render
    render()
