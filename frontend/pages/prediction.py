"""
PowerPilot AI — Predictions Page
Shows ML-based energy consumption predictions with interactive controls
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
      <h2 style="font-family:'Orbitron',monospace; color:#00d4ff;
                 text-shadow:0 0 25px rgba(0,212,255,0.5); letter-spacing:4px;">
        🔮 AI PREDICTIONS
      </h2>
      <p style="color:rgba(232,244,253,0.5); font-size:0.8rem; letter-spacing:2px;">
        RANDOMFOREST REGRESSOR · ENERGY FORECASTING
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        horizon = st.selectbox(
            "Prediction Horizon",
            options=["next_hour", "next_day", "next_7_days"],
            format_func=lambda x: {
                "next_hour": "⏱ Next Hour",
                "next_day": "📅 Next 24 Hours",
                "next_7_days": "📆 Next 7 Days",
            }[x],
        )
    with col3:
        run_btn = st.button("⚡ Run Prediction", use_container_width=True)

    if run_btn:
        with st.spinner("Running ML prediction model..."):
            try:
                resp = requests.get(f"{API_BASE}/predict?horizon={horizon}", timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    _display_prediction(data, horizon)
                else:
                    st.error(f"Prediction failed: {resp.json().get('detail', 'Unknown error')}")
            except requests.ConnectionError:
                st.error("❌ Backend offline. Start: `python backend/app/main.py`")
    else:
        _placeholder_ui(horizon)


def _placeholder_ui(horizon: str):
    horizon_labels = {
        "next_hour": "1 Hour",
        "next_day": "24 Hours",
        "next_7_days": "7 Days",
    }
    st.markdown(f"""
    <div style="text-align:center; padding:60px 20px;
                background:rgba(6,18,42,0.5); border:1px dashed rgba(0,212,255,0.2);
                border-radius:20px; margin-top:20px;">
      <div style="font-size:3rem; margin-bottom:16px;">🔮</div>
      <div style="font-family:'Orbitron',monospace; color:rgba(0,212,255,0.7);
                  font-size:1rem; letter-spacing:3px;">
        PREDICTION READY
      </div>
      <div style="color:rgba(232,244,253,0.4); font-size:0.8rem; margin-top:8px;">
        Click "Run Prediction" to forecast next {horizon_labels[horizon]}
      </div>
    </div>
    """, unsafe_allow_html=True)


def _display_prediction(data: dict, horizon: str):
    predictions = data.get("predictions", [])
    accuracy = data.get("model_accuracy")

    if not predictions:
        st.warning("No predictions returned. Upload energy data first.")
        return

    df = pd.DataFrame(predictions)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Metrics row
    avg_pred = df["predicted_value"].mean()
    max_pred = df["predicted_value"].max()
    min_pred = df["predicted_value"].min()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Data Points", len(df))
    c2.metric("⚡ Avg Predicted", f"{avg_pred:.3f} kWh")
    c3.metric("🔺 Peak Predicted", f"{max_pred:.3f} kWh")
    if accuracy is not None:
        c4.metric("🎯 Model R²", f"{accuracy*100:.1f}%")
    else:
        c4.metric("🔻 Min Predicted", f"{min_pred:.3f} kWh")

    st.markdown("---")

    # Prediction chart
    fig = go.Figure()

    # Confidence band (±10%)
    upper = df["predicted_value"] * 1.1
    lower = df["predicted_value"] * 0.9
    fig.add_trace(go.Scatter(
        x=pd.concat([df["timestamp"], df["timestamp"][::-1]]),
        y=pd.concat([upper, lower[::-1]]),
        fill="toself",
        fillcolor="rgba(123,47,247,0.1)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Confidence Band",
        showlegend=True,
        hoverinfo="skip",
    ))

    # Prediction line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["predicted_value"],
        mode="lines+markers",
        name="Predicted kWh",
        line=dict(color="#7b2ff7", width=2.5),
        marker=dict(color="#7b2ff7", size=5, symbol="circle",
                    line=dict(color="#00d4ff", width=1)),
        fill="tozeroy",
        fillcolor="rgba(123,47,247,0.07)",
        hovertemplate="%{x|%Y-%m-%d %H:%M}<br><b>%{y:.3f} kWh</b><extra></extra>",
    ))

    horizon_titles = {
        "next_hour": "Next 1 Hour Forecast",
        "next_day": "Next 24-Hour Forecast",
        "next_7_days": "7-Day Energy Forecast",
    }
    fig.update_layout(
        title=dict(
            text=f"🔮 {horizon_titles.get(horizon, 'Prediction')}",
            font=dict(family="Orbitron", size=14, color="#7b2ff7"),
        ),
        legend=dict(orientation="h", y=1.05, x=0),
        height=420,
        **CHART_THEME,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Data table
    with st.expander("📋 Raw Prediction Data"):
        df_display = df.copy()
        df_display["timestamp"] = df_display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        df_display["predicted_value"] = df_display["predicted_value"].round(4)
        df_display.columns = ["Timestamp", "Predicted kWh"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
