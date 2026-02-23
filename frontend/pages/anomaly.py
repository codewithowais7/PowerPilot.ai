"""
PowerPilot AI — Anomaly Detection Page
Shows anomaly results with scatter plot, timeline, and statistics
"""
import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_BASE = os.getenv("POWERPILOT_API", "http://localhost:8000/api/v1")

CHART_THEME = dict(
    paper_bgcolor="rgba(3,11,26,0)",
    plot_bgcolor="rgba(6,18,42,0.4)",
    font=dict(family="Exo 2, sans-serif", color="#e8f4fd"),
    xaxis=dict(gridcolor="rgba(0,212,255,0.06)", showline=True, linecolor="rgba(0,212,255,0.2)"),
    yaxis=dict(gridcolor="rgba(0,212,255,0.06)", showline=True, linecolor="rgba(0,212,255,0.2)"),
    margin=dict(l=40, r=20, t=50, b=40),
)


def render():
    st.markdown("""
    <div style="padding: 20px 0 10px;">
      <h2 style="font-family:'Orbitron',monospace; color:#ff3b5b;
                 text-shadow:0 0 25px rgba(255,59,91,0.5); letter-spacing:4px;">
        🚨 ANOMALY DETECTION
      </h2>
      <p style="color:rgba(232,244,253,0.5); font-size:0.8rem; letter-spacing:2px;">
        ISOLATION FOREST · UNSUPERVISED ANOMALY DETECTION
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col2:
        detect_btn = st.button("🚨 Run Detection", use_container_width=True)

    if detect_btn:
        with st.spinner("Running IsolationForest anomaly detection..."):
            try:
                resp = requests.post(f"{API_BASE}/anomalies/detect", timeout=30)
                if resp.status_code == 200:
                    _display_results(resp.json())
                else:
                    st.error(f"Detection failed: {resp.json().get('detail', 'Unknown')}")
            except requests.ConnectionError:
                st.error("❌ Backend offline.")
    else:
        # Try loading existing results
        try:
            resp = requests.get(f"{API_BASE}/anomalies", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data["total_records"] > 0:
                    _display_results(data)
                else:
                    _empty_state()
            else:
                _empty_state()
        except requests.ConnectionError:
            st.warning("⚠️ Backend offline. Start backend to load anomaly data.")


def _empty_state():
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;
                background:rgba(6,18,42,0.5); border:1px dashed rgba(255,59,91,0.2);
                border-radius:20px;">
      <div style="font-size:3rem; margin-bottom:16px;">🚨</div>
      <div style="font-family:'Orbitron',monospace; color:rgba(255,59,91,0.7); letter-spacing:3px;">
        NO ANOMALY DATA
      </div>
      <div style="color:rgba(232,244,253,0.4); font-size:0.8rem; margin-top:8px;">
        Upload data first, then click "Run Detection"
      </div>
    </div>
    """, unsafe_allow_html=True)


def _display_results(data: dict):
    total = data.get("total_records", 0)
    n_anomalies = data.get("total_anomalies", 0)
    rate = data.get("anomaly_rate", 0)
    anomalies = data.get("anomalies", [])

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Total Records", f"{total:,}")
    c2.metric("🚨 Anomalies", f"{n_anomalies:,}")
    c3.metric("📈 Anomaly Rate", f"{rate:.2f}%")
    status_icon = "🔴" if n_anomalies > 0 else "🟢"
    c4.metric("⚡ Status", f"{status_icon} {'ALERT' if n_anomalies > 0 else 'NORMAL'}")

    st.markdown("---")

    if not anomalies:
        st.success("✅ No anomalies detected in your energy data!")
        return

    # Fetch full data for chart
    try:
        full_resp = requests.get(f"http://localhost:8000/api/v1/energy-data?limit=5000", timeout=15)
        if full_resp.status_code == 200:
            df_all = pd.DataFrame(full_resp.json()["data"])
            df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])
            df_all = df_all.sort_values("timestamp")

            anom_df = pd.DataFrame(anomalies)
            anom_df["timestamp"] = pd.to_datetime(anom_df["timestamp"])

            fig = go.Figure()

            # Normal data
            fig.add_trace(go.Scatter(
                x=df_all["timestamp"],
                y=df_all["consumption_kwh"],
                mode="lines",
                name="Normal",
                line=dict(color="rgba(0,212,255,0.5)", width=1),
                fill="tozeroy",
                fillcolor="rgba(0,212,255,0.04)",
                hovertemplate="%{x|%Y-%m-%d %H:%M}<br>%{y:.3f} kWh<extra></extra>",
            ))

            # Anomaly points
            fig.add_trace(go.Scatter(
                x=anom_df["timestamp"],
                y=anom_df["consumption"],
                mode="markers",
                name="⚠️ Anomaly",
                marker=dict(
                    color="#ff3b5b",
                    size=10,
                    symbol="circle",
                    line=dict(color="white", width=1),
                    opacity=0.9,
                ),
                hovertemplate="%{x|%Y-%m-%d %H:%M}<br><b>ANOMALY: %{y:.3f} kWh</b><extra></extra>",
            ))

            fig.update_layout(
                title=dict(text="🚨 Anomaly Detection Results", font=dict(family="Orbitron", size=14, color="#ff3b5b")),
                legend=dict(orientation="h", y=1.05),
                height=420,
                **CHART_THEME,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception:
        pass

    # Anomaly score distribution
    anom_df2 = pd.DataFrame(anomalies)
    if "anomaly_score" in anom_df2.columns and not anom_df2["anomaly_score"].isna().all():
        fig2 = go.Figure(go.Histogram(
            x=anom_df2["anomaly_score"],
            nbinsx=30,
            marker_color="rgba(255,59,91,0.6)",
            marker_line=dict(color="rgba(255,59,91,0.9)", width=1),
            name="Anomaly Score",
        ))
        fig2.update_layout(
            title=dict(text="📊 Anomaly Score Distribution", font=dict(family="Orbitron", size=13, color="#ff3b5b")),
            height=250,
            **CHART_THEME,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Table
    with st.expander(f"📋 Show {n_anomalies} Anomaly Records"):
        display_df = anom_df2[["timestamp", "consumption", "anomaly_score"]].copy()
        display_df.columns = ["Timestamp", "Consumption (kWh)", "Anomaly Score"]
        display_df["Timestamp"] = pd.to_datetime(display_df["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        display_df["Consumption (kWh)"] = display_df["Consumption (kWh)"].round(4)
        display_df["Anomaly Score"] = display_df["Anomaly Score"].round(4)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
