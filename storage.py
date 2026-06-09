"""
storage.py - Persistent storage for StockMetric using local JSON files
Saves watchlist, alerts, and portfolio between sessions
"""

import json
import os

STORAGE_FILE = "stockmetric_data.json"


def load_data() -> dict:
    """Load all saved data from disk."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "watchlist": ["AAPL", "MSFT", "NVDA"],
        "alerts": {},
        "portfolio": {},
    }


def save_data(data: dict):
    """Save all data to disk."""
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error: {e}")


def get_watchlist() -> list:
    return load_data().get("watchlist", [])

def save_watchlist(watchlist: list):
    data = load_data()
    data["watchlist"] = watchlist
    save_data(data)

def get_alerts() -> dict:
    return load_data().get("alerts", {})

def save_alerts(alerts: dict):
    data = load_data()
    data["alerts"] = alerts
    save_data(data)

def get_portfolio() -> dict:
    return load_data().get("portfolio", {})

def save_portfolio(portfolio: dict):
    data = load_data()
    data["portfolio"] = portfolio
    save_data(data)
