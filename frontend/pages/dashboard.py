"""
PowerPilot AI — Dashboard Page
Main overview: energy consumption graph, KPI metrics, CSV upload, recommendations
"""
import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

API_BASE = os.getenv("POWERPILOT_API", "http://localhost:8000/api/v1")

CHART_THEME = dict(
    paper_bgcolor="rgba(3,11,26,0)",
    plot_bgcolor="rgba(6,18,42,0.4)",
    font=dict(family="Exo 2, sans-serif", color="#e8f4fd"),
    xaxis=dict(
        gridcolor="rgba(0,212,255,0.06)",
        showline=True,
        linecolor="rgba(0,212,255,0.2)",
        tickfont=dict(size=10),
    ),
    yaxis=dict(
        gridcolor="rgba(0,212,255,0.06)",
        showline=True,
        linecolor="rgba(0,212,255,0.2)",
        tickfont=dict(size=10),
    ),
    margin=dict(l=40, r=20, t=50, b=40),
)


def page_header():
    # Particle background
    particles_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "components", "particle_background.html")
    if os.path.exists(particles_path):
        with open(particles_path) as f:
            st.components.v1.html(f.read(), height=0)

    st.markdown("""
    <div style="text-align:center; padding:30px 0 20px;">
      <h1 style="font-family:'Orbitron',monospace; font-weight:900; font-size:2.4rem;
                 color:#00d4ff; text-shadow:0 0 40px rgba(0,212,255,0.5),
                 0 0 80px rgba(0,212,255,0.2); letter-spacing:6px; margin:0;">
         POWERPILOT AI
      </h1>
      <p style="font-family:'Exo 2',sans-serif; color:rgba(232,244,253,0.5);
                font-size:0.8rem; letter-spacing:4px; margin-top:8px;">
        SMART ENERGY INTELLIGENCE & OPTIMIZATION PLATFORM
      </p>
    </div>
    """, unsafe_allow_html=True)


def upload_section():
    st.markdown("### 📤 Data Upload")
    uploaded = st.file_uploader(
        "Upload CSV Energy Data",
        type=["csv"],
        help="CSV must contain 'timestamp' and 'consumption_kwh' columns",
        label_visibility="collapsed",
    )
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("⚡ Upload & Process", use_container_width=True):
            if uploaded:
                with st.spinner("Processing data..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/upload-csv",
                            files={"file": (uploaded.name, uploaded.read(), "text/csv")},
                            timeout=60,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(f"✅ {data['message']}")
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {resp.json().get('detail', 'Unknown error')}")
                    except requests.ConnectionError:
                        st.error("❌ Backend not running. Start it with: `python backend/app/main.py`")
            else:
                st.warning("Please select a CSV file first.")


def kpi_metrics():
    try:
        resp = requests.get(f"{API_BASE}/analysis", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("⚡ Daily Usage", f"{data['daily_usage']:.1f} kWh")
            c2.metric("📅 Weekly Usage", f"{data['weekly_usage']:.1f} kWh")
            c3.metric("🗓 Monthly Usage", f"{data['monthly_usage']:.1f} kWh")
            c4.metric("📈 Annual Projection", f"{data['yearly_usage']:.0f} kWh")
            return data
    except Exception:
        pass
    c1, c2, c3, c4 = st.columns(4)
    for c, label in zip([c1, c2, c3, c4], ["Daily", "Weekly", "Monthly", "Annual"]):
        c.metric(f"⚡ {label}", "— kWh", help="Upload data to see metrics")
    return None


def energy_chart():
    try:
        resp = requests.get(f"{API_BASE}/energy-data?limit=1000", timeout=15)
        if resp.status_code == 200:
            raw = resp.json()
            if raw["total"] == 0:
                st.info("📊 No data yet. Upload a CSV file to see your energy chart.")
                return

            df = pd.DataFrame(raw["data"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

            fig = go.Figure()

            # Main consumption line
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["consumption_kwh"],
                mode="lines",
                name="Consumption (kWh)",
                line=dict(color="#00d4ff", width=1.5, smoothing=1.3),
                fill="tozeroy",
                fillcolor="rgba(0,212,255,0.07)",
                hovertemplate="%{x|%Y-%m-%d %H:%M}<br><b>%{y:.3f} kWh</b><extra></extra>",
            ))

            # Rolling average
            df["rolling_avg"] = df["consumption_kwh"].rolling(window=24, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["rolling_avg"],
                mode="lines",
                name="24h Rolling Avg",
                line=dict(color="#7b2ff7", width=2, dash="dot"),
                hovertemplate="%{x|%Y-%m-%d %H:%M}<br>Avg: %{y:.3f} kWh<extra></extra>",
            ))

            fig.update_layout(
                title=dict(text="⚡ Energy Consumption Timeline", font=dict(family="Orbitron", size=14, color="#00d4ff")),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(size=10)),
                height=380,
                **CHART_THEME,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.error("Failed to load energy data.")
    except requests.ConnectionError:
        st.warning("⚠️ Backend offline. Start backend to see charts.")


def recommendations_section(analysis_data):
    if not analysis_data:
        return

    st.markdown("### 💡 AI Recommendations")
    trend = analysis_data.get("trend", "Unknown")
    peak_hours = analysis_data.get("peak_hours", [])

    # Trend badge
    trend_color = "#00ff88" if "Decreas" in trend else ("#ff3b5b" if "Increas" in trend else "#ffb800")
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
      <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem;
                   color:rgba(232,244,253,0.5);">CONSUMPTION TREND:</span>
      <span style="color:{trend_color}; font-family:'Orbitron',monospace;
                   font-size:0.85rem; font-weight:700;
                   text-shadow:0 0 15px {trend_color}66;">{trend}</span>
    </div>
    """, unsafe_allow_html=True)

    recs = analysis_data.get("recommendations", [])
    for rec in recs:
        st.markdown(f"""
        <div style="background:rgba(6,18,42,0.8); border:1px solid rgba(0,212,255,0.15);
                    border-left:3px solid #00d4ff; border-radius:10px; padding:12px 16px;
                    margin:8px 0; font-family:'Exo 2',sans-serif; font-size:0.85rem;
                    color:rgba(232,244,253,0.85);">
          {rec}
        </div>
        """, unsafe_allow_html=True)


def hourly_heatmap():
    try:
        resp = requests.get(f"{API_BASE}/energy-data?limit=5000", timeout=20)
        if resp.status_code != 200 or resp.json()["total"] == 0:
            return
        df = pd.DataFrame(resp.json()["data"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["day_name"] = df["timestamp"].dt.day_name()
        df["hour"] = df["timestamp"].dt.hour

        pivot = df.pivot_table(values="consumption_kwh", index="day_name", columns="hour", aggfunc="mean")
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        pivot = pivot.reindex([d for d in day_order if d in pivot.index])

        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"{h}:00" for h in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[
                [0, "#030b1a"],
                [0.3, "#00244d"],
                [0.6, "#00569c"],
                [0.8, "#00aee0"],
                [1, "#00d4ff"],
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text="kWh", font=dict(color="#e8f4fd", size=10)),
                tickfont=dict(color="#e8f4fd", size=9),
            ),
            hovertemplate="%{y} %{x}<br><b>%{z:.3f} kWh</b><extra></extra>",
        ))
        fig.update_layout(
            title=dict(text="🌡️ Consumption Heatmap (Day × Hour)", font=dict(family="Orbitron", size=13, color="#00d4ff")),
            height=300,
            **CHART_THEME,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception:
        pass


def render():
    page_header()
    st.markdown("---")

    # Upload
    upload_section()
    st.markdown("---")

    # KPI Metrics
    st.markdown("### 📊 Key Performance Indicators")
    analysis = kpi_metrics()
    st.markdown("---")

    # Charts
    col_left, col_right = st.columns([3, 1])
    with col_left:
        energy_chart()
    with col_right:
        if analysis:
            recommendations_section(analysis)

    st.markdown("---")
    hourly_heatmap()
