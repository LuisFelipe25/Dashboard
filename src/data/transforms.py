from __future__ import annotations

from typing import Any

import pandas as pd


def normalize_price_data(price_data: pd.DataFrame) -> pd.DataFrame:
    frame = price_data.copy()
    frame["timestamp"] = pd.to_datetime(frame["time"], utc=True)
    numeric_columns = ["open", "high", "low", "close", "volume", "spread", "real_volume"]
    for column in numeric_columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values("timestamp").reset_index(drop=True)


def signal_status(latest_trade_time: pd.Timestamp | None, reference_time: pd.Timestamp) -> str:
    if latest_trade_time is None or pd.isna(latest_trade_time):
        return "Historical Demo"
    delta_days = (reference_time - latest_trade_time).days
    if delta_days <= 5:
        return "Active"
    if delta_days <= 30:
        return "Monitored"
    return "Historical Demo"


def build_narrative(
    signal_label: str,
    metrics: dict[str, Any],
    windows: dict[str, dict[str, Any]],
    status: str,
    signal_description: str,
) -> str:
    strongest_window = max(windows.items(), key=lambda item: item[1]["return_pct"])
    return (
        f"{signal_label} is presented as a {status.lower()} investor-facing signal profile. "
        f"{signal_description} On a normalized 1,000 USD presentation account, the evaluated sample "
        f"shows {metrics['total_return_pct']:.1f}% cumulative return with a Sharpe ratio of "
        f"{metrics['sharpe_ratio']:.2f} and a maximum drawdown of {abs(metrics['max_drawdown_pct']):.1f}%. "
        f"The strongest recent window was {strongest_window[0]}, where the signal added "
        f"{strongest_window[1]['return_pct']:.1f}% across {strongest_window[1]['trades']} executed trades. "
        f"The emphasis here is not aggressive compounding, but consistency of trade selection, "
        f"controlled capital presentation and a readable execution profile backed by "
        f"{metrics['profit_factor']:.2f} profit factor and {metrics['win_rate_pct']:.1f}% win rate."
    )


def build_provenance_notes(real_artifacts_used: bool) -> list[str]:
    if real_artifacts_used:
        return [
            "Signal timing, entries and exits are loaded from local strategy artifacts when they exist.",
            "Portfolio capital is normalized to a 1,000 USD presentation allocation for investor-facing review.",
            "If any artifact is missing, the app falls back to a generated dataset without breaking the UX.",
        ]
    return [
        "This session is running on generated demo data because one or more real artifacts were not found.",
        "All performance figures remain coherent but hypothetical until real data replaces the sample generator.",
    ]
