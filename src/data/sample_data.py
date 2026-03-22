from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.analytics.equity import build_equity_curve
from src.analytics.metrics import attach_window_returns, build_comparison_table, compute_signal_metrics, compute_window_metrics
from src.analytics.trades import enrich_trade_book
from src.config.settings import AppSettings
from src.data.transforms import build_narrative, build_provenance_notes, signal_status


@dataclass(frozen=True)
class DemoDataset:
    price_data: pd.DataFrame
    signals: dict[str, dict[str, Any]]
    comparison_table: pd.DataFrame
    metadata: dict[str, Any]
    provenance: dict[str, Any]


def _generate_price_frame(rows: int = 24 * 260, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(end=pd.Timestamp.utcnow().floor("h"), periods=rows, freq="h", tz="UTC")
    trend = np.linspace(0, 180, rows)
    cycle = 22 * np.sin(np.linspace(0, 12 * np.pi, rows))
    noise = rng.normal(0, 6.5, rows).cumsum() * 0.12
    close = 2320 + trend + cycle + noise
    open_ = np.roll(close, 1)
    open_[0] = close[0] - 2.1
    high = np.maximum(open_, close) + rng.uniform(1.2, 8.0, rows)
    low = np.minimum(open_, close) - rng.uniform(1.1, 7.6, rows)
    volume = rng.integers(1800, 8200, rows)
    spread = rng.uniform(2, 8, rows)
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "spread": spread,
            "real_volume": np.zeros(rows, dtype=int),
        }
    )


def _trade_rows_from_price_data(price_data: pd.DataFrame, signal_key: str) -> pd.DataFrame:
    rng = np.random.default_rng(11 if signal_key == "baseline_only" else 19)
    spacing = 18 if signal_key == "baseline_only" else 28
    offsets = np.arange(45, len(price_data) - 20, spacing)
    if signal_key == "baseline_plus_ml_filter":
        offsets = offsets[rng.random(len(offsets)) > 0.18]

    rows: list[dict[str, Any]] = []
    for idx, offset in enumerate(offsets):
        entry = price_data.iloc[offset]
        hold = int(rng.integers(4, 22 if signal_key == "baseline_only" else 18))
        exit_idx = min(offset + hold, len(price_data) - 1)
        exit_bar = price_data.iloc[exit_idx]
        drift = (exit_bar["close"] - entry["open"]) * (1.0 if signal_key == "baseline_only" else 1.08)
        edge = rng.normal(0.35 if signal_key == "baseline_plus_ml_filter" else 0.12, 4.1)
        pnl_points = drift + edge
        rows.append(
            {
                "Size": 0.25,
                "EntryBar": int(offset),
                "ExitBar": int(exit_idx),
                "EntryPrice": float(entry["open"]),
                "ExitPrice": float(exit_bar["close"]),
                "SL": np.nan,
                "TP": np.nan,
                "PnL": pnl_points,
                "Commission": 0.0,
                "ReturnPct": 0.0,
                "EntryTime": entry["timestamp"],
                "ExitTime": exit_bar["timestamp"],
                "Duration": exit_bar["timestamp"] - entry["timestamp"],
                "Tag": "",
                "Entry_λ(C)": 0.0,
                "Exit_λ(C)": 0.0,
                "Entry_atr_func(H,L,C,14)": 0.0,
                "Exit_atr_func(H,L,C,14)": 0.0,
                "variant_name": signal_key,
                "fold_id": idx // 24,
            }
        )
    return pd.DataFrame(rows)


def generate_demo_dataset(settings: AppSettings) -> DemoDataset:
    price_data = _generate_price_frame()
    signal_payloads: dict[str, dict[str, Any]] = {}

    for signal_key, style in settings.signal_styles.items():
        raw_trades = _trade_rows_from_price_data(price_data, signal_key)
        trades = enrich_trade_book(raw_trades, signal_key, settings)
        equity_curve, trades = build_equity_curve(trades, price_data, settings.initial_capital)
        latest_time = price_data["timestamp"].max()
        windows = {
            label: compute_window_metrics(
                trades,
                equity_curve,
                latest_time - pd.Timedelta(days=days),
                settings.initial_capital,
            )
            for label, days in settings.time_windows.items()
        }
        metrics = attach_window_returns(
            compute_signal_metrics(trades, equity_curve, settings.initial_capital),
            windows,
        )
        status = signal_status(metrics["latest_trade_time"], latest_time)
        signal_payloads[signal_key] = {
            "key": signal_key,
            "label": style.label,
            "style": style,
            "trades": trades,
            "equity_curve": equity_curve,
            "metrics": metrics,
            "windows": windows,
            "status": status,
            "narrative": build_narrative(
                style.label,
                metrics,
                windows,
                status,
                style.description,
            ),
        }

    return DemoDataset(
        price_data=price_data,
        signals=signal_payloads,
        comparison_table=build_comparison_table(signal_payloads, settings),
        metadata={
            "source_mode": "generated_demo",
            "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        },
        provenance={
            "mode": "generated_demo",
            "real_artifacts_used": False,
            "notes": build_provenance_notes(False),
        },
    )
