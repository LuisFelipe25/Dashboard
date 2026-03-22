from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.analytics.equity import build_equity_curve
from src.analytics.metrics import attach_window_returns, build_comparison_table, compute_signal_metrics, compute_window_metrics
from src.analytics.trades import enrich_trade_book
from src.config.settings import AppSettings
from src.data.sample_data import DemoDataset, generate_demo_dataset
from src.data.transforms import build_narrative, build_provenance_notes, normalize_price_data, signal_status


@dataclass(frozen=True)
class DashboardDataset:
    price_data: pd.DataFrame
    signals: dict[str, dict[str, Any]]
    comparison_table: pd.DataFrame
    metadata: dict[str, Any]
    provenance: dict[str, Any]


def _latest_directory(path: Path) -> Path | None:
    if not path.exists():
        return None
    directories = [candidate for candidate in path.iterdir() if candidate.is_dir()]
    if not directories:
        return None
    return max(directories, key=lambda item: item.name)


def _latest_price_csv(path: Path) -> Path | None:
    if not path.exists():
        return None
    candidates = sorted(path.glob("XAUUSD_H1_*.csv"))
    return candidates[-1] if candidates else None


def _load_real_artifact_dataset(settings: AppSettings) -> DashboardDataset:
    latest_run_dir = _latest_directory(settings.fusion_outputs_dir)
    latest_price_csv = _latest_price_csv(settings.price_data_dir)
    if latest_run_dir is None or latest_price_csv is None:
        raise FileNotFoundError("Missing fusion integration outputs or price CSV.")

    executed_trades_path = latest_run_dir / "executed_trades.csv"
    summary_path = latest_run_dir / "summary.json"
    if not executed_trades_path.exists() or not summary_path.exists():
        raise FileNotFoundError("Required artifact files were not found.")

    raw_trades = pd.read_csv(executed_trades_path)
    price_data = normalize_price_data(pd.read_csv(latest_price_csv))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    latest_time = price_data["timestamp"].max()

    signal_payloads: dict[str, dict[str, Any]] = {}
    for signal_key, style in settings.signal_styles.items():
        signal_trades = raw_trades.loc[raw_trades["variant_name"] == signal_key].copy()
        trades = enrich_trade_book(signal_trades, signal_key, settings)
        equity_curve, trades = build_equity_curve(trades, price_data, settings.initial_capital)
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

    summary_by_variant = {item["variant_name"]: item for item in summary.get("variants", [])}
    for signal_key, payload in signal_payloads.items():
        variant_summary = summary_by_variant.get(signal_key, {})
        payload["ml_aux_metric"] = {
            "label": "Metrica ML complementaria",
            "value": variant_summary.get("candidate_trades", 0),
            "blocked_candidates": variant_summary.get("blocked_candidates", 0),
        }

    return DashboardDataset(
        price_data=price_data,
        signals=signal_payloads,
        comparison_table=build_comparison_table(signal_payloads, settings),
        metadata={
            "source_mode": "artifact_backed",
            "latest_run_dir": str(latest_run_dir),
            "latest_price_csv": str(latest_price_csv),
            "summary_project": summary.get("project_name"),
            "summary_label": summary.get("run_label"),
            "generated_at_utc": summary.get("generated_at_utc"),
            "overlap_start": summary.get("overlap_start"),
            "overlap_end": summary.get("overlap_end"),
        },
        provenance={
            "mode": "artifact_backed",
            "real_artifacts_used": True,
            "notes": build_provenance_notes(True),
        },
    )


def load_dashboard_dataset(settings: AppSettings) -> DashboardDataset:
    try:
        return _load_real_artifact_dataset(settings)
    except Exception as exc:
        demo: DemoDataset = generate_demo_dataset(settings)
        metadata = demo.metadata | {"fallback_reason": str(exc)}
        return DashboardDataset(
            price_data=demo.price_data,
            signals=demo.signals,
            comparison_table=demo.comparison_table,
            metadata=metadata,
            provenance=demo.provenance,
        )
