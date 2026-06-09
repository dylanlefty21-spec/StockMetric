"""
analyzer.py - StockMetric Analysis Engine
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


def fetch_stock(ticker: str, period: str = "6mo"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval="1d")
    if df.empty:
        raise ValueError(f"No data found for {ticker}")
    if df.index.tzinfo is not None:
        df.index = df.index.tz_localize(None)
    return df


def get_stock_info(ticker: str):
    try:
        info = yf.Ticker(ticker).info
        return {
            "name":       info.get("longName", ticker),
            "sector":     info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap", None),
            "pe_ratio":   info.get("trailingPE", None),
            "52w_high":   info.get("fiftyTwoWeekHigh", None),
            "52w_low":    info.get("fiftyTwoWeekLow", None),
            "description": info.get("longBusinessSummary", "")[:300] if info.get("longBusinessSummary") else "",
        }
    except Exception:
        return {"name": ticker, "sector": "Unknown", "market_cap": None,
                "pe_ratio": None, "52w_high": None, "52w_low": None, "description": ""}


# ── Indicators ────────────────────────────────────────────────────────────────

def rsi(close, period=14):
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def macd(close, fast=12, slow=26, sig=9):
    ema_f  = close.ewm(span=fast, adjust=False).mean()
    ema_s  = close.ewm(span=slow, adjust=False).mean()
    line   = ema_f - ema_s
    signal = line.ewm(span=sig, adjust=False).mean()
    return line, signal

def adx(df, period=14):
    h, l, c  = df["High"], df["Low"], df["Close"]
    plus_dm  = h.diff().clip(lower=0)
    minus_dm = (-l.diff()).clip(lower=0)
    tr       = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    atr      = tr.ewm(span=period, adjust=False).mean()
    plus_di  = 100 * plus_dm.ewm(span=period, adjust=False).mean() / (atr + 1e-9)
    minus_di = 100 * minus_dm.ewm(span=period, adjust=False).mean() / (atr + 1e-9)
    dx       = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9)
    return dx.ewm(span=period, adjust=False).mean(), plus_di, minus_di

def bollinger(close, period=20):
    mid = close.rolling(period).mean()
    std = close.rolling(period).std()
    return mid + 2*std, mid, mid - 2*std

def atr_pct(df, period=14):
    h, l, c = df["High"], df["Low"], df["Close"]
    tr  = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(span=period, adjust=False).mean()
    return (atr / c * 100).iloc[-1]


# ── Main Analysis ─────────────────────────────────────────────────────────────

def analyze(ticker: str) -> dict:
    df   = fetch_stock(ticker)
    info = get_stock_info(ticker)
    close = df["Close"]
    n     = len(close)

    df["rsi"]              = rsi(close)
    df["macd"], df["msig"] = macd(close)
    df["adx"], df["pdi"], df["mdi"] = adx(df)
    df["bb_up"], df["bb_mid"], df["bb_lo"] = bollinger(close)
    df["ema20"]  = close.ewm(span=20, adjust=False).mean()
    df["ema50"]  = close.ewm(span=50, adjust=False).mean()
    df["ema200"] = close.ewm(span=200, adjust=False).mean()
    df["vol20"]  = df["Volume"].rolling(20).mean()

    last  = df.iloc[-1]
    price = float(last["Close"])
    prev  = float(df.iloc[-2]["Close"])

    trend_checks = {
        "Price above 20-day average":   price > last["ema20"],
        "Price above 50-day average":   price > last["ema50"],
        "Price above 200-day average":  price > last["ema200"],
        "Short-term EMA > Long-term":   last["ema20"] > last["ema50"],
        "ADX shows strong trend":       last["adx"] > 25,
        "Buyers stronger than sellers": last["pdi"] > last["mdi"],
        "Price up vs 1 month ago":      price > float(df["Close"].iloc[-21]) if n > 21 else False,
        "Price up vs 3 months ago":     price > float(df["Close"].iloc[-63]) if n > 63 else False,
    }
    trend_score = int(sum(trend_checks.values()) / len(trend_checks) * 100)

    buy_checks = {
        "RSI not overbought (< 70)":  last["rsi"] < 70,
        "RSI not oversold (> 30)":    last["rsi"] > 30,
        "MACD crossing up":           last["macd"] > last["msig"],
        "Price near lower BB (value)": price < last["bb_mid"],
        "Volume above average":       last["Volume"] > last["vol20"],
        "Momentum positive":          price > prev,
        "ADX trending (> 20)":        last["adx"] > 20,
        "RSI in sweet spot (40-65)":  40 < last["rsi"] < 65,
    }
    buy_score = int(sum(buy_checks.values()) / len(buy_checks) * 100)

    daily_vol = close.pct_change().std() * np.sqrt(252) * 100
    atr_p     = atr_pct(df)
    rsi_val   = float(last["rsi"])

    risk_checks = {
        "Low daily volatility (< 30%)":  daily_vol < 30,
        "Price not near 52w high":        price < (info["52w_high"] or price*1.1) * 0.95,
        "RSI not overbought":             rsi_val < 75,
        "Not below lower Bollinger":      price > last["bb_lo"],
        "ATR % manageable (< 3%)":        atr_p < 3,
        "Volume not spiking (< 3x avg)":  last["Volume"] < last["vol20"] * 3,
        "Above 200-day average":          price > last["ema200"],
    }
    risk_score = int(sum(risk_checks.values()) / len(risk_checks) * 100)

    def color(score):
        if score >= 60: return "green"
        if score >= 40: return "yellow"
        return "red"

    overall = int((trend_score * 0.4) + (buy_score * 0.35) + (risk_score * 0.25))

    if overall >= 65:
        verdict, verdict_color = "BULLISH", "green"
        verdict_text = "This stock looks strong. Conditions are favorable."
    elif overall >= 45:
        verdict, verdict_color = "NEUTRAL", "yellow"
        verdict_text = "Mixed signals — not clearly bullish or bearish right now."
    else:
        verdict, verdict_color = "BEARISH", "red"
        verdict_text = "This stock is showing weakness. Better to wait and watch."

    change_1d = (price - prev) / prev * 100
    change_1w = (price - float(df["Close"].iloc[-6]))  / float(df["Close"].iloc[-6])  * 100 if n > 6  else 0
    change_1m = (price - float(df["Close"].iloc[-22])) / float(df["Close"].iloc[-22]) * 100 if n > 22 else 0

    # Signal history — last 90 days of verdicts for accuracy tracking
    history_signals = []
    for i in range(90, 0, -5):
        if i >= n: continue
        sl = df.iloc[:n-i]
        if len(sl) < 30: continue
        sl_last = sl.iloc[-1]
        sl_price = float(sl_last["Close"])
        sl_prev  = float(sl.iloc[-2]["Close"])
        tc = sum([
            sl_price > float(sl_last["ema20"]),
            sl_price > float(sl_last["ema50"]),
            sl_last["macd"] > sl_last["msig"],
            sl_last["pdi"]  > sl_last["mdi"],
        ])
        bc = sum([
            sl_last["rsi"] < 70,
            sl_last["rsi"] > 30,
            sl_last["macd"] > sl_last["msig"],
            sl_price > sl_prev,
        ])
        ov = int((tc/4*0.5 + bc/4*0.5) * 100)
        sig = "BULLISH" if ov >= 65 else ("BEARISH" if ov < 45 else "NEUTRAL")
        # Check if prediction was correct (price went up in next period)
        future_idx = n - i + 5
        if future_idx < n:
            future_price = float(df["Close"].iloc[future_idx])
            correct = (sig == "BULLISH" and future_price > sl_price) or \
                      (sig == "BEARISH" and future_price < sl_price)
            history_signals.append({"date": sl.index[-1], "signal": sig, "correct": correct})

    accuracy = 0
    if history_signals:
        accuracy = sum(1 for h in history_signals if h["correct"]) / len(history_signals) * 100

    return {
        "ticker":        ticker.upper(),
        "name":          info["name"],
        "sector":        info["sector"],
        "description":   info["description"],
        "price":         price,
        "change_1d":     change_1d,
        "change_1w":     change_1w,
        "change_1m":     change_1m,
        "trend_score":   trend_score,
        "buy_score":     buy_score,
        "risk_score":    risk_score,
        "overall":       overall,
        "trend_color":   color(trend_score),
        "buy_color":     color(buy_score),
        "risk_color":    color(risk_score),
        "verdict":       verdict,
        "verdict_color": verdict_color,
        "verdict_text":  verdict_text,
        "trend_checks":  trend_checks,
        "buy_checks":    buy_checks,
        "risk_checks":   risk_checks,
        "rsi":           float(last["rsi"]),
        "adx":           float(last["adx"]),
        "macd_val":      float(last["macd"]),
        "macd_sig":      float(last["msig"]),
        "ema20":         float(last["ema20"]),
        "ema50":         float(last["ema50"]),
        "ema200":        float(last["ema200"]),
        "vol_ann":       daily_vol,
        "atr_pct":       atr_p,
        "52w_high":      info["52w_high"],
        "52w_low":       info["52w_low"],
        "accuracy":      accuracy,
        "df":            df,
    }


# ── Stock of the Day ──────────────────────────────────────────────────────────

SP500_SAMPLE = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B","JPM","V",
    "UNH","XOM","LLY","JNJ","MA","PG","HD","MRK","AVGO","CVX",
    "PEP","ABBV","KO","COST","WMT","MCD","BAC","CRM","TMO","CSCO",
    "ACN","ABT","DHR","TXN","NEE","PM","RTX","ADBE","NFLX","LIN",
]

def get_stock_of_the_day():
    """Screen a sample of S&P 500 stocks and return the top bullish pick."""
    import datetime
    # Use date as seed so it's consistent for the whole day
    seed = int(datetime.date.today().strftime("%Y%m%d"))
    np.random.seed(seed)
    candidates = np.random.choice(SP500_SAMPLE, size=15, replace=False).tolist()

    best = None
    best_score = -1
    for t in candidates:
        try:
            r = analyze(t)
            if r["overall"] > best_score:
                best_score = r["overall"]
                best = r
        except Exception:
            pass
    return best
