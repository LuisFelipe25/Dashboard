from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SignalStyle:
    key: str
    label: str
    accent: str
    soft_accent: str
    description: str
    headline: str
    scale_factor: float
    status_hint: str


@dataclass(frozen=True)
class AppSettings:
    project_root: Path
    initial_capital: float = 10_000.0
    pip_factor: float = 10.0
    chart_lookback_days: int = 120
    primary_chart_height: int = 440
    candle_chart_height: int = 620
    app_name: str = "Quant Signal Performance Suite"
    app_tagline: str = "AI-Assisted Trading Signal Intelligence"
    app_subtitle: str = (
        "Commercial demo console for presenting execution-grade trading signals "
        "with premium analytics, investor-facing storytelling and deployment-ready UX."
    )
    artifact_mode_label: str = "Real artifacts + demo capital normalization"
    signal_styles: dict[str, SignalStyle] = field(
        default_factory=lambda: {
            "baseline_only": SignalStyle(
                key="baseline_only",
                label="Signal 1",
                accent="#42D7C7",
                soft_accent="rgba(66, 215, 199, 0.16)",
                description=(
                    "High-coverage baseline flow focused on opportunity capture and "
                    "broad market participation."
                ),
                headline="Broader market participation with institutional-style monitoring.",
                scale_factor=4.8,
                status_hint="Monitored",
            ),
            "baseline_plus_ml_filter": SignalStyle(
                key="baseline_plus_ml_filter",
                label="Signal 2",
                accent="#F7B955",
                soft_accent="rgba(247, 185, 85, 0.16)",
                description=(
                    "Selective baseline enhanced with an ML validation layer to reduce "
                    "noise and focus capital on higher-conviction setups."
                ),
                headline="Selective flow with an ML filter designed to reduce noise.",
                scale_factor=8.0,
                status_hint="Monitored",
            ),
        }
    )
    time_windows: dict[str, int] = field(
        default_factory=lambda: {"1M": 30, "3M": 90, "6M": 180}
    )

    @property
    def assets_dir(self) -> Path:
        return self.project_root / "assets"

    @property
    def fusion_outputs_dir(self) -> Path:
        return self.project_root / "Fusion_Integration" / "outputs" / "latest"

    @property
    def price_data_dir(self) -> Path:
        return self.project_root / "Estrategia_Trading" / "data" / "raw"

    @property
    def ml_outputs_dir(self) -> Path:
        return self.project_root / "Comparacion_ML" / "outputs"

    @property
    def comparison_metrics(self) -> tuple[str, ...]:
        return (
            "total_return_pct",
            "sharpe_ratio",
            "max_drawdown_pct",
            "profit_factor",
            "win_rate_pct",
            "total_trades",
            "net_pips",
        )

    @property
    def comparison_labels(self) -> dict[str, str]:
        return {
            "total_return_pct": "Return",
            "sharpe_ratio": "Sharpe",
            "max_drawdown_pct": "Max DD",
            "profit_factor": "Profit Factor",
            "win_rate_pct": "Win Rate",
            "total_trades": "Trades",
            "net_pips": "Net Pips",
        }


def get_app_settings() -> AppSettings:
    project_root = Path(__file__).resolve().parents[2]
    return AppSettings(project_root=project_root)
