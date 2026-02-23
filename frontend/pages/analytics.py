"""
PowerPilot AI — Analytics Page
Deep-dive analytics: daily/monthly trends, hourly profiles, weekend vs weekday analysis
"""
import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_BASE = os.getenv("POWERPILOT_API", "http://localhost:8000/api/v1")

# ─── Shared chart layout helper ───────────────────────────────────────────────
# We use a function instead of a dict so each call gets a fresh copy,
# avoiding **kwargs conflicts when charts add their own xaxis/yaxis overrides.

def _base_layout(title_text: str, title_color: str = "#00ff88", height: int = 350) -> dict:
    return dict(
        title=dict(
            text=title_text,
            font=dict(family="Orbitron, monospace", size=13, color=title_color),
        ),
        height=height,
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
        margin=dict(l=50, r=20, t=60, b=40),
    )


def render():
    st.markdown("""
    <div style="padding: 20px 0 10px;">
      <h2 style="font-family:'Orbitron',monospace; color:#00ff88;
                 text-shadow:0 0 25px rgba(0,255,136,0.4); letter-spacing:4px;">
        📊 ADVANCED ANALYTICS
      </h2>
      <p style="color:rgba(232,244,253,0.5); font-size:0.8rem; letter-spacing:2px;">
        DEEP-DIVE ENERGY INTELLIGENCE
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Load data from backend
    try:
        resp = requests.get(f"{API_BASE}/energy-data?limit=10000", timeout=20)
        if resp.status_code != 200:
            st.error(f"Backend returned status {resp.status_code}")
            return
        payload = resp.json()
        if payload.get("total", 0) == 0:
            st.info("📊 Upload energy data on the Dashboard to see analytics.")
            return
        df = pd.DataFrame(payload["data"])
    except requests.ConnectionError:
        st.warning("⚠️ Backend offline. Start it with: `python -m uvicorn backend.app.main:app --port 8000`")
        return
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return

    # Parse and derive columns
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["date"]       = df["timestamp"].dt.date
    df["year_month"] = df["timestamp"].dt.to_period("M").astype(str)
    df["day_name"]   = df["timestamp"].dt.day_name()

    # Render each section
    _hourly_profile(df)
    st.markdown("---")
    _daily_trend(df)
    st.markdown("---")
    _monthly_bar(df)
    st.markdown("---")
    _weekend_vs_weekday(df)
    st.markdown("---")
    _summary_stats(df)


# ─── Chart: Hourly Profile ────────────────────────────────────────────────────
def _hourly_profile(df: pd.DataFrame):
    hourly = df.groupby("hour")["consumption_kwh"].agg(["mean", "std", "max"]).reset_index()
    hourly["std"] = hourly["std"].fillna(0)

    fig = go.Figure()

    # Confidence band (±1 std)
    upper = hourly["mean"] + hourly["std"]
    lower = (hourly["mean"] - hourly["std"]).clip(lower=0)
    fig.add_trace(go.Scatter(
        x=list(hourly["hour"]) + list(hourly["hour"][::-1]),
        y=list(upper) + list(lower[::-1]),
        fill="toself",
        fillcolor="rgba(0,212,255,0.1)",
        line=dict(color="rgba(0,0,0,0)"),
        name="±1 Std Dev",
        showlegend=True,
        hoverinfo="skip",
    ))

    # Average line
    fig.add_trace(go.Scatter(
        x=hourly["hour"], y=hourly["mean"],
        mode="lines+markers", name="Avg kWh",
        line=dict(color="#00d4ff", width=2.5),
        marker=dict(size=6, color="#00d4ff"),
        hovertemplate="Hour %{x}:00<br>Avg: %{y:.3f} kWh<extra></extra>",
    ))

    # Max line
    fig.add_trace(go.Scatter(
        x=hourly["hour"], y=hourly["max"],
        mode="lines", name="Max kWh",
        line=dict(color="#ff3b5b", width=1.5, dash="dot"),
        hovertemplate="Hour %{x}:00<br>Max: %{y:.3f} kWh<extra></extra>",
    ))

    layout = _base_layout("⏰ Hourly Consumption Profile", "#00ff88", 350)
    # Override xaxis tick labels for hours
    layout["xaxis"]["tickmode"] = "array"
    layout["xaxis"]["tickvals"] = list(range(24))
    layout["xaxis"]["ticktext"] = [f"{h}h" for h in range(24)]
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─── Chart: Daily Trend ───────────────────────────────────────────────────────
def _daily_trend(df: pd.DataFrame):
    daily = df.groupby("date")["consumption_kwh"].sum().reset_index()
    daily.columns = ["date", "total_kwh"]
    daily["date"] = pd.to_datetime(daily["date"])
    daily["rolling_7d"] = daily["total_kwh"].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["date"], y=daily["total_kwh"],
        name="Daily Total",
        marker_color="rgba(0,212,255,0.4)",
        marker_line=dict(color="rgba(0,212,255,0.7)", width=0.5),
        hovertemplate="%{x|%Y-%m-%d}<br>Total: %{y:.2f} kWh<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["rolling_7d"],
        mode="lines", name="7-Day Rolling Avg",
        line=dict(color="#00ff88", width=2.5),
        hovertemplate="%{x|%Y-%m-%d}<br>7d Avg: %{y:.2f} kWh<extra></extra>",
    ))
    layout = _base_layout("📅 Daily Energy Consumption Trend", "#00ff88", 350)
    layout["barmode"] = "overlay"
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─── Chart: Monthly Bar ───────────────────────────────────────────────────────
def _monthly_bar(df: pd.DataFrame):
    monthly = df.groupby("year_month")["consumption_kwh"].sum().reset_index()
    monthly.columns = ["Month", "Total_kWh"]

    fig = go.Figure(go.Bar(
        x=monthly["Month"],
        y=monthly["Total_kWh"],
        marker=dict(
            color=monthly["Total_kWh"],
            colorscale=[[0, "#00244d"], [0.5, "#00569c"], [1, "#00d4ff"]],
            showscale=False,
            line=dict(color="rgba(0,212,255,0.5)", width=1),
        ),
        hovertemplate="%{x}<br>Total: %{y:.2f} kWh<extra></extra>",
    ))
    fig.update_layout(**_base_layout("🗓️ Monthly Energy Consumption", "#00ff88", 320))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─── Chart: Weekend vs Weekday ────────────────────────────────────────────────
def _weekend_vs_weekday(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    # Donut pie
    with col1:
        we_mask = df["is_weekend"] == True
        wd_mask = df["is_weekend"] == False
        avg_we = df.loc[we_mask, "consumption_kwh"].mean() if we_mask.any() else 0
        avg_wd = df.loc[wd_mask, "consumption_kwh"].mean() if wd_mask.any() else 0

        fig = go.Figure(go.Pie(
            labels=["Weekday", "Weekend"],
            values=[avg_wd, avg_we],
            hole=0.55,
            marker=dict(
                colors=["#00d4ff", "#7b2ff7"],
                line=dict(color="#030b1a", width=2),
            ),
            textfont=dict(family="Exo 2, sans-serif", size=12),
            hovertemplate="%{label}<br>Avg: %{value:.3f} kWh<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text="📊 Weekday vs Weekend", font=dict(family="Orbitron, monospace", size=12, color="#00ff88")),
            paper_bgcolor="rgba(3,11,26,0)",
            font=dict(color="#e8f4fd", family="Exo 2, sans-serif"),
            showlegend=True,
            height=280,
            margin=dict(t=50, b=10, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Day-of-week bar
    with col2:
        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        dow = df.groupby("day")["consumption_kwh"].mean().reset_index()
        dow["day_name"] = dow["day"].map(dict(enumerate(day_labels)))

        bar_colors = (
            ["rgba(0,212,255,0.6)"] * min(5, len(dow))
            + ["rgba(123,47,247,0.6)"] * max(0, len(dow) - 5)
        )

        fig2 = go.Figure(go.Bar(
            x=dow["day_name"],
            y=dow["consumption_kwh"],
            marker=dict(
                color=bar_colors,
                line=dict(color="rgba(0,212,255,0.4)", width=1),
            ),
            hovertemplate="%{x}<br>Avg: %{y:.3f} kWh<extra></extra>",
        ))
        fig2.update_layout(
            title=dict(text="📆 Day of Week Profile", font=dict(family="Orbitron, monospace", size=12, color="#00ff88")),
            paper_bgcolor="rgba(3,11,26,0)",
            plot_bgcolor="rgba(6,18,42,0.4)",
            font=dict(color="#e8f4fd", family="Exo 2, sans-serif"),
            xaxis=dict(gridcolor="rgba(0,212,255,0.06)", showline=True, linecolor="rgba(0,212,255,0.2)"),
            yaxis=dict(gridcolor="rgba(0,212,255,0.06)", showline=True, linecolor="rgba(0,212,255,0.2)"),
            height=280,
            margin=dict(t=50, b=30, l=50, r=10),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


# ─── Summary Stats ────────────────────────────────────────────────────────────
def _summary_stats(df: pd.DataFrame):
    st.markdown("### 📋 Statistical Summary")
    stats = df["consumption_kwh"].describe()
    cols = st.columns(6)
    labels = ["Count", "Mean", "Std Dev", "Min", "Median", "Max"]
    values = [
        f"{int(stats['count']):,}",
        f"{stats['mean']:.3f}",
        f"{stats['std']:.3f}",
        f"{stats['min']:.3f}",
        f"{stats['50%']:.3f}",
        f"{stats['max']:.3f}",
    ]
    for col, label, val in zip(cols, labels, values):
        col.metric(label, f"{val} kWh" if label != "Count" else val)
