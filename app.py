"""
app.py - StockMetric
Beginner-friendly stock analysis platform
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import time

st.set_page_config(
    page_title="StockMetric",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
ACCENT   = "#6366f1"   # indigo
GREEN    = "#22c55e"
YELLOW   = "#f59e0b"
RED      = "#ef4444"
BG       = "#0f1117"
CARD     = "#1a1d2e"
CARD2    = "#222640"
BORDER   = "#2e3150"
TEXT     = "#e2e8f0"
SUBTEXT  = "#94a3b8"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: {BG}; color: {TEXT}; }}
.stApp {{ background: {BG}; }}
[data-testid="stSidebar"] {{ background: #0d0f1a; border-right: 1px solid {BORDER}; }}
.stButton button {{ background: {ACCENT} !important; color: white !important; border-radius: 10px !important; font-weight: 600 !important; border: none !important; padding: 10px 20px !important; }}
.stTextInput input {{ background: {CARD} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; border-radius: 10px !important; }}
.stNumberInput input {{ background: {CARD} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; border-radius: 8px !important; }}
.stSlider {{ color: {ACCENT}; }}
div[data-testid="stMetric"] {{ background: {CARD}; border-radius: 12px; padding: 16px; border: 1px solid {BORDER}; }}
div[data-testid="stMetric"] label {{ color: {SUBTEXT} !important; font-size: 11px !important; letter-spacing: 1px !important; }}

/* Cards */
.sm-card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; padding: 20px 24px; }}
.sm-card-accent {{ background: {CARD}; border: 1px solid {ACCENT}; border-radius: 16px; padding: 20px 24px; }}

/* Score */
.score-wrap {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; padding: 20px; }}
.score-num-green  {{ font-size: 48px; font-weight: 800; color: {GREEN};  font-family: JetBrains Mono, monospace; line-height:1; }}
.score-num-yellow {{ font-size: 48px; font-weight: 800; color: {YELLOW}; font-family: JetBrains Mono, monospace; line-height:1; }}
.score-num-red    {{ font-size: 48px; font-weight: 800; color: {RED};    font-family: JetBrains Mono, monospace; line-height:1; }}
.score-label {{ font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: {SUBTEXT}; margin-bottom: 6px; }}
.score-desc  {{ font-size: 13px; color: {SUBTEXT}; margin-top: 8px; line-height: 1.5; }}

/* Bar */
.bar-bg    {{ background: #1e2235; border-radius: 999px; height: 8px; margin: 8px 0; overflow: hidden; }}
.bar-green  {{ background: {GREEN};  height: 100%; border-radius: 999px; }}
.bar-yellow {{ background: {YELLOW}; height: 100%; border-radius: 999px; }}
.bar-red    {{ background: {RED};    height: 100%; border-radius: 999px; }}

/* Verdict */
.verdict-green  {{ background: linear-gradient(135deg, #052e16, #14532d); border: 2px solid {GREEN};  border-radius: 16px; padding: 24px; text-align: center; }}
.verdict-yellow {{ background: linear-gradient(135deg, #1c1108, #451a03); border: 2px solid {YELLOW}; border-radius: 16px; padding: 24px; text-align: center; }}
.verdict-red    {{ background: linear-gradient(135deg, #1c0a0a, #450a0a); border: 2px solid {RED};    border-radius: 16px; padding: 24px; text-align: center; }}
.verdict-val-green  {{ font-size: 40px; font-weight: 800; color: {GREEN};  }}
.verdict-val-yellow {{ font-size: 40px; font-weight: 800; color: {YELLOW}; }}
.verdict-val-red    {{ font-size: 40px; font-weight: 800; color: {RED};    }}
.verdict-sub {{ font-size: 14px; color: {SUBTEXT}; margin-top: 6px; }}

/* Checklist */
.chk-row {{ display:flex; align-items:center; justify-content:space-between; padding:9px 0; border-bottom:1px solid {BORDER}; font-size:13px; color:{TEXT}; }}
.chk-pass {{ color:{GREEN}; font-weight:600; }}
.chk-fail {{ color:{RED}; }}

/* Tooltip */
.tooltip-wrap {{ position: relative; display: inline-block; cursor: help; }}
.tooltip-icon {{ color: {ACCENT}; font-size: 12px; margin-left: 4px; }}
.tooltip-text {{ visibility: hidden; background: #1e2235; color: {TEXT}; font-size: 12px; border-radius: 8px; padding: 8px 12px; position: absolute; z-index: 99; bottom: 125%; left: 50%; transform: translateX(-50%); width: 220px; border: 1px solid {BORDER}; line-height: 1.5; }}
.tooltip-wrap:hover .tooltip-text {{ visibility: visible; }}

/* Pills */
.pill-green  {{ background: #14532d; color: {GREEN};  padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.pill-yellow {{ background: #451a03; color: {YELLOW}; padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
.pill-red    {{ background: #450a0a; color: {RED};    padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; }}

/* Section label */
.sec-label {{ font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: {SUBTEXT}; margin: 28px 0 14px; padding-bottom: 8px; border-bottom: 1px solid {BORDER}; }}

/* Watchlist */
.wl-item {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }}

/* SOTD */
.sotd-card {{ background: linear-gradient(135deg, {CARD}, {CARD2}); border: 1px solid {ACCENT}; border-radius: 16px; padding: 24px; }}

/* Price */
.price-up   {{ color: {GREEN}; font-weight: 600; }}
.price-down {{ color: {RED};   font-weight: 600; }}

/* Education */
.edu-card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; padding: 20px; margin-bottom: 12px; }}
.edu-term {{ font-size: 16px; font-weight: 700; color: {ACCENT}; margin-bottom: 6px; }}
.edu-def  {{ font-size: 14px; color: {SUBTEXT}; line-height: 1.6; }}

/* Logo */
.logo {{ font-size: 22px; font-weight: 800; background: linear-gradient(90deg, {ACCENT}, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
</style>
""", unsafe_allow_html=True)


# ── Tooltip helper ─────────────────────────────────────────────────────────────
TOOLTIPS = {
    "RSI":         "RSI (Relative Strength Index) measures momentum. Above 70 = overbought (may drop). Below 30 = oversold (may bounce). Sweet spot is 40–65.",
    "ADX":         "ADX measures trend strength. Above 25 means a real trend exists. Below 20 means the stock is moving sideways with no clear direction.",
    "Volatility":  "How wildly the stock price swings. Under 20% = calm and stable. Over 40% = wild and risky. Higher volatility = higher potential gain AND loss.",
    "EMA":         "Exponential Moving Average. A smoothed average price over time. When price is above its EMA, that's a bullish sign.",
    "MACD":        "MACD compares two moving averages to show momentum. When the MACD line crosses above the signal line, that's a buy signal.",
    "Bollinger":   "Bollinger Bands show a price range. When price touches the lower band, it may be undervalued. Upper band = may be overvalued.",
    "52w High":    "The highest price the stock reached in the last 52 weeks (1 year). Trading near this level can mean strong momentum — or that it's due for a pullback.",
    "Stop Loss":   "A price level where you automatically sell to limit your loss. A 3% stop loss means you exit if the price drops 3% from where you bought.",
}

def tooltip(term):
    tip = TOOLTIPS.get(term, "")
    return f"""<span class='tooltip-wrap'><span class='tooltip-icon'>ⓘ</span>
    <span class='tooltip-text'>{tip}</span></span>"""


# ── Watchlist (session-based) ──────────────────────────────────────────────────
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = ["AAPL", "MSFT", "NVDA"]


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='logo'>📊 StockMetric</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:12px; color:#475569; margin-bottom:20px;'>Smart stock analysis for everyone</div>", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("", [
        "🏠  Home",
        "🔬  Deep Dive",
        "📊  Compare",
        "⭐  Watchlist",
        "📚  Learn",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:11px; color:{SUBTEXT}; line-height:1.8;'>
    <span style='color:{GREEN}; font-weight:700;'>● GREEN (60–100)</span> Strong signal<br>
    <span style='color:{YELLOW}; font-weight:700;'>● YELLOW (40–59)</span> Mixed signals<br>
    <span style='color:{RED}; font-weight:700;'>● RED (0–39)</span> Weak signal<br><br>
    <span style='color:#475569; font-size:10px;'>⚠️ Not financial advice.</span>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════
#  HOME PAGE
# ════════════════════════════════════════════
if "Home" in page:
    # Hero
    st.markdown(f"""
    <div style='padding: 40px 0 20px; text-align: center;'>
      <div style='font-size: 52px; font-weight: 800;
                  background: linear-gradient(90deg, {ACCENT}, #38bdf8, {GREEN});
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  line-height: 1.1; margin-bottom: 12px;'>
        StockMetric
      </div>
      <div style='font-size: 18px; color: {SUBTEXT}; margin-bottom: 32px;'>
        Simple, powerful stock analysis for beginner investors
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick search
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        quick_ticker = st.text_input("", placeholder="🔍  Search a stock ticker (e.g. AAPL, TSLA, NVDA)",
                                     label_visibility="collapsed")
        if st.button("Analyze →", use_container_width=True) and quick_ticker:
            st.session_state["deep_ticker"] = quick_ticker.upper().strip()
            st.session_state["deep_result"] = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Stock of the Day
    st.markdown("<div class='sec-label'>⭐ STOCK OF THE DAY</div>", unsafe_allow_html=True)

    if "sotd" not in st.session_state:
        with st.spinner("Finding today's top pick from the S&P 500..."):
            from analyzer import get_stock_of_the_day
            st.session_state["sotd"] = get_stock_of_the_day()

    sotd = st.session_state["sotd"]
    if sotd:
        vc = sotd["verdict_color"]
        chg_arrow = "▲" if sotd["change_1d"] >= 0 else "▼"
        chg_color = GREEN if sotd["change_1d"] >= 0 else RED
        st.markdown(f"""
        <div class='sotd-card'>
          <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;'>
            <div>
              <div style='font-size:11px; font-weight:700; letter-spacing:2px; color:{ACCENT}; margin-bottom:4px;'>TODAY'S TOP PICK</div>
              <div style='font-size:28px; font-weight:800; color:{TEXT};'>{sotd['ticker']}</div>
              <div style='font-size:14px; color:{SUBTEXT}; margin-top:2px;'>{sotd['name']} · {sotd['sector']}</div>
            </div>
            <div style='text-align:right;'>
              <div style='font-size:32px; font-weight:700; font-family:JetBrains Mono,monospace; color:{TEXT};'>${sotd['price']:.2f}</div>
              <div style='color:{chg_color}; font-weight:600;'>{chg_arrow} {abs(sotd['change_1d']):.2f}% today</div>
            </div>
          </div>
          <div style='display:flex; gap:16px; margin-top:20px; flex-wrap:wrap;'>
            <div style='background:#1e2235; border-radius:10px; padding:12px 20px; flex:1; min-width:100px; text-align:center;'>
              <div style='font-size:11px; color:{SUBTEXT};'>OVERALL</div>
              <div style='font-size:28px; font-weight:800; color:{GREEN if sotd["overall"]>=60 else (YELLOW if sotd["overall"]>=40 else RED)}; font-family:JetBrains Mono,monospace;'>{sotd['overall']}</div>
            </div>
            <div style='background:#1e2235; border-radius:10px; padding:12px 20px; flex:1; min-width:100px; text-align:center;'>
              <div style='font-size:11px; color:{SUBTEXT};'>TREND</div>
              <div style='font-size:28px; font-weight:800; color:{GREEN if sotd["trend_color"]=="green" else (YELLOW if sotd["trend_color"]=="yellow" else RED)}; font-family:JetBrains Mono,monospace;'>{sotd['trend_score']}</div>
            </div>
            <div style='background:#1e2235; border-radius:10px; padding:12px 20px; flex:1; min-width:100px; text-align:center;'>
              <div style='font-size:11px; color:{SUBTEXT};'>BUY TIMING</div>
              <div style='font-size:28px; font-weight:800; color:{GREEN if sotd["buy_color"]=="green" else (YELLOW if sotd["buy_color"]=="yellow" else RED)}; font-family:JetBrains Mono,monospace;'>{sotd['buy_score']}</div>
            </div>
            <div style='background:#1e2235; border-radius:10px; padding:12px 20px; flex:1; min-width:100px; text-align:center;'>
              <div style='font-size:11px; color:{SUBTEXT};'>RISK</div>
              <div style='font-size:28px; font-weight:800; color:{GREEN if sotd["risk_color"]=="green" else (YELLOW if sotd["risk_color"]=="yellow" else RED)}; font-family:JetBrains Mono,monospace;'>{sotd['risk_score']}</div>
            </div>
          </div>
          <div style='margin-top:16px; font-size:14px; color:{SUBTEXT};'>{sotd['verdict_text']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works
    st.markdown("<div class='sec-label'>HOW STOCKMETRIC WORKS</div>", unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4)
    steps = [
        ("🔍", "Search", "Type any stock ticker like AAPL or TSLA"),
        ("🧠", "Analyze", "We run 23 checks across trend, timing, and risk"),
        ("🎨", "Color Code", "Green, yellow, or red tells you the verdict instantly"),
        ("📈", "Decide", "Use the scores and checklist to make an informed choice"),
    ]
    for col, (icon, title, desc) in zip([h1, h2, h3, h4], steps):
        with col:
            st.markdown(f"""<div class='sm-card' style='text-align:center;'>
              <div style='font-size:28px; margin-bottom:8px;'>{icon}</div>
              <div style='font-weight:700; font-size:15px; color:{TEXT}; margin-bottom:4px;'>{title}</div>
              <div style='font-size:13px; color:{SUBTEXT};'>{desc}</div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
#  DEEP DIVE PAGE
# ════════════════════════════════════════════
elif "Deep Dive" in page:
    st.markdown(f"<h2 style='font-weight:800; color:{TEXT}; margin-bottom:4px;'>🔬 Deep Dive</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SUBTEXT}; margin-bottom:20px;'>Full analysis of a single stock</p>", unsafe_allow_html=True)

    ci, cb = st.columns([3, 1])
    with ci:
        ticker_input = st.text_input("", placeholder="Enter ticker (e.g. AAPL)",
                                     value=st.session_state.get("deep_ticker", "AAPL"),
                                     label_visibility="collapsed").upper().strip()
    with cb:
        go_btn = st.button("Analyze →", use_container_width=True)

    if go_btn or ("deep_result" not in st.session_state) or (st.session_state.get("deep_ticker") != ticker_input):
        with st.spinner(f"Analyzing {ticker_input}..."):
            try:
                from analyzer import analyze
                result = analyze(ticker_input)
                st.session_state["deep_result"] = result
                st.session_state["deep_ticker"] = ticker_input
            except Exception as e:
                st.error(f"❌ Could not load **{ticker_input}**. Please check the ticker symbol and try again.")
                st.stop()

    r = st.session_state.get("deep_result")
    if not r:
        st.stop()

    # Add to watchlist button
    wl = st.session_state["watchlist"]
    if r["ticker"] not in wl:
        if st.button(f"⭐ Add {r['ticker']} to Watchlist"):
            st.session_state["watchlist"].append(r["ticker"])
            st.success(f"Added {r['ticker']} to your watchlist!")

    # ── Price Row ──
    st.markdown("<div class='sec-label'>PRICE OVERVIEW</div>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)

    def chg(val):
        a = "▲" if val >= 0 else "▼"
        c = GREEN if val >= 0 else RED
        return f"<span style='color:{c}; font-weight:700;'>{a} {abs(val):.2f}%</span>"

    with p1:
        st.markdown(f"""<div class='sm-card'>
          <div style='font-size:12px; color:{SUBTEXT}; font-weight:600; letter-spacing:1px;'>{r['ticker']} · {r['sector']}</div>
          <div style='font-size:14px; color:{TEXT}; margin:2px 0 4px;'>{r['name']}</div>
          <div style='font-size:34px; font-weight:800; font-family:JetBrains Mono,monospace; color:{TEXT};'>${r['price']:.2f}</div>
        </div>""", unsafe_allow_html=True)
    with p2:
        st.markdown(f"""<div class='sm-card' style='text-align:center;'>
          <div style='font-size:11px; color:{SUBTEXT}; font-weight:700; letter-spacing:1px; margin-bottom:8px;'>TODAY</div>
          <div style='font-size:26px; font-weight:700;'>{chg(r['change_1d'])}</div>
        </div>""", unsafe_allow_html=True)
    with p3:
        st.markdown(f"""<div class='sm-card' style='text-align:center;'>
          <div style='font-size:11px; color:{SUBTEXT}; font-weight:700; letter-spacing:1px; margin-bottom:8px;'>1 WEEK</div>
          <div style='font-size:26px; font-weight:700;'>{chg(r['change_1w'])}</div>
        </div>""", unsafe_allow_html=True)
    with p4:
        st.markdown(f"""<div class='sm-card' style='text-align:center;'>
          <div style='font-size:11px; color:{SUBTEXT}; font-weight:700; letter-spacing:1px; margin-bottom:8px;'>1 MONTH</div>
          <div style='font-size:26px; font-weight:700;'>{chg(r['change_1m'])}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Verdict + Accuracy ──
    st.markdown("<div class='sec-label'>OVERALL VERDICT</div>", unsafe_allow_html=True)
    v1, v2 = st.columns([2, 1])

    with v1:
        vc = r['verdict_color']
        st.markdown(f"""<div class='verdict-{vc}'>
          <div style='font-size:11px; font-weight:700; letter-spacing:2px; color:{SUBTEXT}; margin-bottom:6px;'>OUR ASSESSMENT</div>
          <div class='verdict-val-{vc}'>{r['verdict']}</div>
          <div class='verdict-sub'>{r['verdict_text']}</div>
        </div>""", unsafe_allow_html=True)

    with v2:
        acc_color = GREEN if r['accuracy'] >= 60 else (YELLOW if r['accuracy'] >= 45 else RED)
        st.markdown(f"""<div class='sm-card' style='text-align:center; height:100%;'>
          <div style='font-size:11px; font-weight:700; letter-spacing:2px; color:{SUBTEXT}; margin-bottom:8px;'>SIGNAL ACCURACY</div>
          <div style='font-size:42px; font-weight:800; font-family:JetBrains Mono,monospace; color:{acc_color};'>{r['accuracy']:.0f}%</div>
          <div style='font-size:12px; color:{SUBTEXT}; margin-top:4px;'>Historical accuracy of<br>signals on this stock</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3 Scores ──
    st.markdown("<div class='sec-label'>THE 3 KEY SCORES</div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)

    score_descs = {
        "trend":  {"📈 Trend Score": "Is this stock going up or down overall?"},
        "buy":    {"🛒 Buy Timing":  "Is right now a good time to buy?"},
        "risk":   {"🛡️ Risk Score":  "How stable and safe is this stock?"},
    }

    def score_card(title, score, color, desc):
        color_map = {"green": GREEN, "yellow": YELLOW, "red": RED}
        c = color_map[color]
        return f"""<div class='score-wrap'>
          <div class='score-label'>{title}</div>
          <div class='score-num-{color}'>{score}</div>
          <div style='font-size:11px; color:{SUBTEXT}; font-family:JetBrains Mono,monospace;'>out of 100</div>
          <div class='bar-bg'><div class='bar-{color}' style='width:{score}%;'></div></div>
          <div class='score-desc'>{desc}</div>
        </div>"""

    trend_descs = {"green": "📈 Strong uptrend — price consistently rising", "yellow": "↗️ Mild uptrend — some positive momentum", "red": "📉 Downtrend — price is falling"}
    buy_descs   = {"green": "✅ Good conditions to consider buying", "yellow": "⚠️ Mixed signals — not the clearest entry", "red": "🚫 Not a great time to buy right now"}
    risk_descs  = {"green": "🟢 Lower risk — relatively stable", "yellow": "🟡 Moderate risk — some caution advised", "red": "🔴 Higher risk — volatile stock"}

    with s1: st.markdown(score_card("📈 TREND SCORE",  r['trend_score'], r['trend_color'], trend_descs[r['trend_color']]), unsafe_allow_html=True)
    with s2: st.markdown(score_card("🛒 BUY TIMING",   r['buy_score'],   r['buy_color'],   buy_descs[r['buy_color']]),     unsafe_allow_html=True)
    with s3: st.markdown(score_card("🛡️ RISK SCORE",   r['risk_score'],  r['risk_color'],  risk_descs[r['risk_color']]),   unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Checklists ──
    st.markdown("<div class='sec-label'>WHAT'S DRIVING EACH SCORE</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    def checklist(checks):
        rows = ""
        for name, passed in checks.items():
            icon = "✅" if passed else "❌"
            cls  = "chk-pass" if passed else "chk-fail"
            rows += f"<div class='chk-row'><span>{name}</span><span class='{cls}'>{icon}</span></div>"
        return f"<div style='background:{CARD}; border:1px solid {BORDER}; border-radius:12px; padding:16px;'>{rows}</div>"

    with c1:
        st.markdown(f"<div style='font-weight:700; color:{TEXT}; margin-bottom:8px;'>📈 Trend Checks</div>", unsafe_allow_html=True)
        st.markdown(checklist(r['trend_checks']), unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='font-weight:700; color:{TEXT}; margin-bottom:8px;'>🛒 Buy Timing Checks</div>", unsafe_allow_html=True)
        st.markdown(checklist(r['buy_checks']), unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='font-weight:700; color:{TEXT}; margin-bottom:8px;'>🛡️ Risk Checks</div>", unsafe_allow_html=True)
        st.markdown(checklist(r['risk_checks']), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart ──
    st.markdown("<div class='sec-label'>PRICE CHART</div>", unsafe_allow_html=True)
    df = r["df"].tail(120)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3], vertical_spacing=0.04)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color=GREEN, decreasing_line_color=RED,
        name="Price", showlegend=False,
    ), row=1, col=1)

    for col, color, name, dash in [("ema20", ACCENT, "20-day avg", "solid"),
                                    ("ema50", YELLOW, "50-day avg", "dash"),
                                    ("ema200", RED, "200-day avg", "dot")]:
        fig.add_trace(go.Scatter(x=df.index, y=df[col],
            line=dict(color=color, width=1.5, dash=dash), name=name), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["bb_up"],
        line=dict(color=BORDER, width=0.8, dash="dot"), name="Upper Band", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_lo"],
        line=dict(color=BORDER, width=0.8, dash="dot"),
        fill="tonexty", fillcolor="rgba(99,102,241,0.04)", name="Lower Band", showlegend=False), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"],
        line=dict(color=ACCENT, width=1.5), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color=RED,   opacity=0.4, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color=GREEN, opacity=0.4, row=2, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(99,102,241,0.04)", line_width=0, row=2, col=1)

    fig.update_layout(
        height=500, paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(family="Inter, sans-serif", color=SUBTEXT, size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=12, orientation="h", y=1.05),
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=10, b=0), hovermode="x unified",
    )
    for i in range(1, 3):
        fig.update_xaxes(gridcolor=BORDER, showline=False, row=i, col=1)
        fig.update_yaxes(gridcolor=BORDER, showline=False, row=i, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # ── Key Numbers ──
    st.markdown("<div class='sec-label'>KEY NUMBERS EXPLAINED</div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    def kpi(label, value, explain, tip_key=None):
        tip = tooltip(tip_key) if tip_key else ""
        return f"""<div class='sm-card'>
          <div style='font-size:11px; color:{SUBTEXT}; font-weight:700; letter-spacing:1px;'>{label}{tip}</div>
          <div style='font-size:26px; font-weight:800; font-family:JetBrains Mono,monospace; color:{TEXT}; margin:6px 0;'>{value}</div>
          <div style='font-size:12px; color:{SUBTEXT};'>{explain}</div>
        </div>"""

    rsi_explain = "🔴 Overbought" if r['rsi'] > 70 else ("🟡 Oversold" if r['rsi'] < 30 else "🟢 Healthy range")
    adx_explain = "Strong trend" if r['adx'] > 25 else ("Weak trend" if r['adx'] < 20 else "Moderate trend")
    dist_52h = ((r['52w_high'] or r['price']) - r['price']) / (r['52w_high'] or r['price']) * 100 if r['52w_high'] else 0

    with k1: st.markdown(kpi("RSI", f"{r['rsi']:.0f}", rsi_explain, "RSI"), unsafe_allow_html=True)
    with k2: st.markdown(kpi("ADX", f"{r['adx']:.0f}", adx_explain, "ADX"), unsafe_allow_html=True)
    with k3: st.markdown(kpi("Annual Volatility", f"{r['vol_ann']:.1f}%", "< 20% stable · > 40% wild", "Volatility"), unsafe_allow_html=True)
    with k4: st.markdown(kpi("From 52w High", f"-{dist_52h:.1f}%", "Distance from yearly peak", "52w High"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stop Loss Calculator ──
    st.markdown("<div class='sec-label'>🛑 STOP LOSS CALCULATOR</div>", unsafe_allow_html=True)

    sl1, sl2 = st.columns([1, 2])
    with sl1:
        entry_price = st.number_input("Entry Price ($)", min_value=0.01,
                                      value=float(round(r['price'], 2)), step=0.01, format="%.2f")
        sl_pct = st.slider("Stop Loss %", 1, 15, 3)
        st.markdown(f"<div style='font-size:12px; color:{SUBTEXT};'>{tooltip('Stop Loss')} What is a stop loss?</div>", unsafe_allow_html=True)

    stop_price    = entry_price * (1 - sl_pct / 100)
    dollar_risk_1 = entry_price - stop_price

    with sl2:
        sizes     = [1000, 5000, 10000]
        size_html = ""
        for size in sizes:
            shares   = size / entry_price
            max_loss = shares * dollar_risk_1
            size_html += f"""<div style='background:{BG}; border-radius:10px; padding:14px 18px; flex:1; min-width:110px;'>
              <div style='font-size:11px; color:{SUBTEXT};'>${size:,} invested</div>
              <div style='font-size:12px; color:{SUBTEXT}; margin:2px 0;'>{shares:.1f} shares</div>
              <div style='font-size:20px; font-weight:700; color:{RED}; font-family:JetBrains Mono,monospace;'>-${max_loss:.0f}</div>
              <div style='font-size:10px; color:{SUBTEXT};'>max loss</div>
            </div>"""

        buffer = ((r['price'] - stop_price) / r['price']) * 100 if r['price'] > stop_price else 0
        st.markdown(f"""
        <div style='background:#2d0f0f; border:2px solid {RED}; border-radius:14px; padding:20px 24px;'>
          <div style='font-size:11px; font-weight:700; letter-spacing:2px; color:{RED}; margin-bottom:14px;'>STOP LOSS LEVELS</div>
          <div style='display:flex; gap:28px; flex-wrap:wrap; margin-bottom:16px;'>
            <div>
              <div style='font-size:11px; color:{SUBTEXT};'>ENTRY PRICE</div>
              <div style='font-size:30px; font-weight:800; font-family:JetBrains Mono,monospace; color:{TEXT};'>${entry_price:.2f}</div>
            </div>
            <div style='display:flex; align-items:center; color:{SUBTEXT}; font-size:20px;'>→</div>
            <div>
              <div style='font-size:11px; color:{SUBTEXT};'>STOP PRICE ({sl_pct}%)</div>
              <div style='font-size:30px; font-weight:800; font-family:JetBrains Mono,monospace; color:{RED};'>${stop_price:.2f}</div>
            </div>
            <div>
              <div style='font-size:11px; color:{SUBTEXT};'>LOSS PER SHARE</div>
              <div style='font-size:30px; font-weight:800; font-family:JetBrains Mono,monospace; color:{RED};'>-${dollar_risk_1:.2f}</div>
            </div>
          </div>
          <div style='font-size:11px; font-weight:700; letter-spacing:2px; color:{SUBTEXT}; margin-bottom:10px;'>MAX LOSS BY POSITION SIZE</div>
          <div style='display:flex; gap:12px; flex-wrap:wrap;'>{size_html}</div>
          <div style='margin-top:14px; padding:12px 14px; background:{CARD}; border-radius:10px; font-size:13px; color:{SUBTEXT};'>
            💡 The stop loss triggers if price drops from
            <b style='color:{TEXT};'>${r['price']:.2f}</b> to
            <b style='color:{RED};'>${stop_price:.2f}</b> — a buffer of
            <b style='color:{TEXT};'>{buffer:.1f}%</b> from today's price.
          </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════
#  COMPARE PAGE
# ════════════════════════════════════════════
elif "Compare" in page:
    st.markdown(f"<h2 style='font-weight:800; color:{TEXT};'>📊 Compare Stocks</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SUBTEXT}; margin-bottom:20px;'>Screen multiple stocks side by side</p>", unsafe_allow_html=True)

    raw = st.text_input("", value="AAPL, MSFT, NVDA, TSLA, AMZN",
                        placeholder="Enter tickers separated by commas",
                        label_visibility="collapsed")
    screen_btn = st.button("Screen All →", use_container_width=False)

    if screen_btn or "screen_results" not in st.session_state:
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()][:10]
        results = []
        prog = st.progress(0, text="Analyzing...")
        from analyzer import analyze
        for i, t in enumerate(tickers):
            prog.progress((i+1)/len(tickers), text=f"Analyzing {t}...")
            try:
                results.append(analyze(t))
            except Exception:
                pass
            time.sleep(0.2)
        prog.empty()
        st.session_state["screen_results"] = sorted(results, key=lambda x: x["overall"], reverse=True)

    results = st.session_state.get("screen_results", [])
    if not results:
        st.stop()

    # Verdict pills row
    st.markdown("<div class='sec-label'>QUICK VERDICT</div>", unsafe_allow_html=True)
    cols = st.columns(len(results))
    for i, r in enumerate(results):
        with cols[i]:
            vc = r['verdict_color']
            chg_c = GREEN if r['change_1d'] >= 0 else RED
            chg_a = "▲" if r['change_1d'] >= 0 else "▼"
            st.markdown(f"""<div class='sm-card' style='text-align:center;'>
              <div style='font-size:20px; font-weight:800; color:{TEXT};'>{r['ticker']}</div>
              <div style='font-size:12px; color:{SUBTEXT}; margin:2px 0 8px;'>${r['price']:.2f} <span style='color:{chg_c};'>{chg_a}{abs(r['change_1d']):.1f}%</span></div>
              <span class='pill-{vc}'>{r['verdict']}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Table
    st.markdown("<div class='sec-label'>SIDE-BY-SIDE SCORES</div>", unsafe_allow_html=True)

    def pill(score, color):
        return f"<span class='pill-{color}'>{score}</span>"

    table = f"<div style='background:{CARD}; border:1px solid {BORDER}; border-radius:16px; overflow:hidden;'>"
    table += f"<table style='width:100%; border-collapse:collapse; font-size:14px;'>"
    table += f"""<tr style='background:{CARD2}; border-bottom:1px solid {BORDER};'>
        <th style='padding:14px 16px; text-align:left; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>STOCK</th>
        <th style='padding:14px 16px; text-align:center; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>PRICE</th>
        <th style='padding:14px 16px; text-align:center; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>TODAY</th>
        <th style='padding:14px 16px; text-align:center; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>📈 TREND</th>
        <th style='padding:14px 16px; text-align:center; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>🛒 BUY</th>
        <th style='padding:14px 16px; text-align:center; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>🛡️ RISK</th>
        <th style='padding:14px 16px; text-align:center; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>OVERALL</th>
        <th style='padding:14px 16px; text-align:center; font-size:11px; letter-spacing:1px; color:{SUBTEXT}; font-weight:700;'>VERDICT</th>
    </tr>"""

    for r in results:
        cc = GREEN if r['change_1d'] >= 0 else RED
        ca = "▲" if r['change_1d'] >= 0 else "▼"
        ov_c = GREEN if r['overall'] >= 60 else (YELLOW if r['overall'] >= 40 else RED)
        table += f"""<tr style='border-bottom:1px solid {BORDER};'>
            <td style='padding:14px 16px;'>
              <div style='font-weight:800; font-size:16px; color:{TEXT};'>{r['ticker']}</div>
              <div style='font-size:11px; color:{SUBTEXT};'>{r['name'][:28]}</div>
            </td>
            <td style='padding:14px 16px; text-align:center; font-family:JetBrains Mono,monospace; font-weight:600; color:{TEXT};'>${r['price']:.2f}</td>
            <td style='padding:14px 16px; text-align:center; color:{cc}; font-weight:700;'>{ca} {abs(r['change_1d']):.2f}%</td>
            <td style='padding:14px 16px; text-align:center;'>{pill(r['trend_score'], r['trend_color'])}</td>
            <td style='padding:14px 16px; text-align:center;'>{pill(r['buy_score'], r['buy_color'])}</td>
            <td style='padding:14px 16px; text-align:center;'>{pill(r['risk_score'], r['risk_color'])}</td>
            <td style='padding:14px 16px; text-align:center; font-weight:800; font-size:20px; font-family:JetBrains Mono,monospace; color:{ov_c};'>{r['overall']}</td>
            <td style='padding:14px 16px; text-align:center;'><span class='pill-{r["verdict_color"]}'>{r['verdict']}</span></td>
        </tr>"""
    table += "</table></div>"
    st.markdown(table, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bar chart
    st.markdown("<div class='sec-label'>SCORE COMPARISON</div>", unsafe_allow_html=True)
    tlist = [r['ticker'] for r in results]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="📈 Trend", x=tlist, y=[r['trend_score'] for r in results],
        marker_color=ACCENT, text=[r['trend_score'] for r in results], textposition="outside", textfont_color=TEXT))
    fig2.add_trace(go.Bar(name="🛒 Buy Timing", x=tlist, y=[r['buy_score'] for r in results],
        marker_color=YELLOW, text=[r['buy_score'] for r in results], textposition="outside", textfont_color=TEXT))
    fig2.add_trace(go.Bar(name="🛡️ Risk", x=tlist, y=[r['risk_score'] for r in results],
        marker_color=GREEN, text=[r['risk_score'] for r in results], textposition="outside", textfont_color=TEXT))

    fig2.add_hline(y=60, line_dash="dash", line_color=GREEN, opacity=0.4, annotation_text="Good (60)")
    fig2.add_hline(y=40, line_dash="dash", line_color=YELLOW, opacity=0.4, annotation_text="Caution (40)")

    fig2.update_layout(barmode="group", height=360,
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(family="Inter, sans-serif", color=SUBTEXT, size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.08, font_color=TEXT),
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis=dict(range=[0, 120], gridcolor=BORDER),
        xaxis=dict(gridcolor=BORDER),
    )
    st.plotly_chart(fig2, use_container_width=True)

    best = results[0]
    st.markdown(f"""
    <div style='background:linear-gradient(135deg, #052e16, #14532d); border:1px solid {GREEN};
                border-radius:14px; padding:20px 24px;'>
      <div style='font-size:11px; font-weight:700; letter-spacing:2px; color:{GREEN}; margin-bottom:6px;'>🏆 TOP PICK FROM YOUR LIST</div>
      <div style='font-size:22px; font-weight:800; color:{TEXT};'>{best['ticker']} — {best['name']}</div>
      <div style='font-size:14px; color:{SUBTEXT}; margin-top:4px;'>Overall Score: <b style='color:{TEXT};'>{best['overall']}/100</b> · {best['verdict_text']}</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════
#  WATCHLIST PAGE
# ════════════════════════════════════════════
elif "Watchlist" in page:
    st.markdown(f"<h2 style='font-weight:800; color:{TEXT};'>⭐ Watchlist</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SUBTEXT}; margin-bottom:20px;'>Your saved stocks at a glance</p>", unsafe_allow_html=True)

    wl = st.session_state["watchlist"]

    # Add ticker
    a1, a2 = st.columns([3, 1])
    with a1:
        new_ticker = st.text_input("", placeholder="Add a ticker to your watchlist",
                                   label_visibility="collapsed").upper().strip()
    with a2:
        if st.button("+ Add", use_container_width=True) and new_ticker:
            if new_ticker not in wl:
                wl.append(new_ticker)
                st.success(f"Added {new_ticker}!")
            else:
                st.info(f"{new_ticker} is already in your watchlist.")

    if not wl:
        st.info("Your watchlist is empty. Add some tickers above!")
        st.stop()

    # Analyze watchlist
    if st.button("🔄 Refresh All", use_container_width=False):
        st.session_state.pop("wl_results", None)

    if "wl_results" not in st.session_state:
        wl_results = []
        prog = st.progress(0, text="Loading watchlist...")
        from analyzer import analyze
        for i, t in enumerate(wl):
            prog.progress((i+1)/len(wl), text=f"Loading {t}...")
            try:
                wl_results.append(analyze(t))
            except Exception:
                pass
        prog.empty()
        st.session_state["wl_results"] = wl_results

    wl_results = st.session_state.get("wl_results", [])

    st.markdown("<div class='sec-label'>YOUR STOCKS</div>", unsafe_allow_html=True)
    for r in wl_results:
        vc   = r['verdict_color']
        cc   = GREEN if r['change_1d'] >= 0 else RED
        ca   = "▲" if r['change_1d'] >= 0 else "▼"
        ov_c = GREEN if r['overall'] >= 60 else (YELLOW if r['overall'] >= 40 else RED)

        col_main, col_remove = st.columns([10, 1])
        with col_main:
            st.markdown(f"""
            <div style='background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
                        padding:16px 20px; margin-bottom:10px;
                        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;'>
              <div>
                <span style='font-size:18px; font-weight:800; color:{TEXT};'>{r['ticker']}</span>
                <span style='font-size:12px; color:{SUBTEXT}; margin-left:8px;'>{r['name'][:30]}</span>
              </div>
              <div style='display:flex; gap:20px; align-items:center; flex-wrap:wrap;'>
                <div style='text-align:center;'>
                  <div style='font-size:11px; color:{SUBTEXT};'>PRICE</div>
                  <div style='font-weight:700; font-family:JetBrains Mono,monospace; color:{TEXT};'>${r['price']:.2f}</div>
                </div>
                <div style='text-align:center;'>
                  <div style='font-size:11px; color:{SUBTEXT};'>TODAY</div>
                  <div style='font-weight:700; color:{cc};'>{ca}{abs(r['change_1d']):.2f}%</div>
                </div>
                <div style='text-align:center;'>
                  <div style='font-size:11px; color:{SUBTEXT};'>SCORE</div>
                  <div style='font-size:22px; font-weight:800; font-family:JetBrains Mono,monospace; color:{ov_c};'>{r['overall']}</div>
                </div>
                <span class='pill-{vc}'>{r['verdict']}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        with col_remove:
            if st.button("✕", key=f"rm_{r['ticker']}"):
                st.session_state["watchlist"].remove(r["ticker"])
                st.session_state.pop("wl_results", None)
                st.rerun()


# ════════════════════════════════════════════
#  LEARN PAGE
# ════════════════════════════════════════════
elif "Learn" in page:
    st.markdown(f"<h2 style='font-weight:800; color:{TEXT};'>📚 Learn</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SUBTEXT}; margin-bottom:20px;'>Plain English explanations of every term in StockMetric</p>", unsafe_allow_html=True)

    concepts = [
        ("📈 Trend Score", "A score from 0–100 measuring whether a stock is going up or down. It looks at whether the current price is above its moving averages and whether buyers are stronger than sellers. A score above 60 means the stock has been consistently rising."),
        ("🛒 Buy Timing Score", "A score that measures whether RIGHT NOW is a good time to buy. Even a stock in a great uptrend can be temporarily overbought. This score uses RSI, MACD, and volume to find the best entry windows."),
        ("🛡️ Risk Score", "A score measuring how safe or volatile a stock is. A high score means the stock moves calmly and predictably. A low score means it's swinging wildly — higher potential gains but also higher potential losses."),
        ("RSI (Relative Strength Index)", "A number from 0–100 measuring price momentum. Above 70 means the stock is 'overbought' — it may be due for a pullback. Below 30 means 'oversold' — it may be due for a bounce. The sweet spot is 40–65."),
        ("Moving Averages (EMA 20/50/200)", "A smoothed average of the stock price over the last 20, 50, or 200 days. When the current price is ABOVE these lines, that's bullish. When price is BELOW them, that's bearish. The 200-day average is the most important one."),
        ("MACD", "MACD stands for Moving Average Convergence Divergence. It compares two moving averages to show momentum. When the MACD line crosses above the signal line, it's considered a buy signal."),
        ("ADX (Average Directional Index)", "ADX measures how STRONG a trend is, not which direction. Above 25 means a strong trend exists. Below 20 means the stock is drifting sideways with no clear direction."),
        ("Bollinger Bands", "Two lines drawn above and below the moving average that represent a normal price range. When price touches the LOWER band, it may be undervalued. When it touches the UPPER band, it may be overvalued."),
        ("Stop Loss", "A predetermined price where you sell a stock to limit your loss. For example, if you buy at $100 with a 3% stop loss, you automatically sell at $97 to prevent further losses. It's one of the most important risk management tools."),
        ("52-Week High/Low", "The highest and lowest price the stock has traded at in the last year. Trading near the 52-week high can mean strong momentum — but also that a pullback may be coming. Near the 52-week low can mean it's beaten down — but may also mean something is fundamentally wrong."),
        ("Volume", "How many shares are traded in a day. High volume on an up day is a bullish sign — lots of buyers. High volume on a down day is bearish. Low volume moves are less reliable."),
        ("Bullish vs Bearish", "Bullish means you expect the price to go UP — like a bull charging forward. Bearish means you expect the price to go DOWN — like a bear swiping downward. These are the two most common terms in investing."),
    ]

    for term, definition in concepts:
        st.markdown(f"""<div class='edu-card'>
          <div class='edu-term'>{term}</div>
          <div class='edu-def'>{definition}</div>
        </div>""", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center; color:#334155; font-size:11px; padding: 32px 0 8px;
            border-top: 1px solid {BORDER}; margin-top: 32px;'>
  StockMetric · Built for beginner investors · ⚠️ Not financial advice · Always do your own research
</div>
""", unsafe_allow_html=True)
