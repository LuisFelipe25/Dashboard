from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.analytics import charts
from src.analytics.metrics import compute_window_metrics
from src.analytics.trades import trade_table_view
from src.config.settings import AppSettings
from src.ui.components import dataframe_with_formatting, metric_card, render_metric_row, section_heading
from src.ui.formatters import format_integer, format_money, format_pct, format_pips


RANGE_OPTIONS = ("1M", "3M", "6M", "2026+", "All")


def render_topbar(settings: AppSettings) -> None:
    st.markdown(f"<div class='eyebrow'>{settings.app_tagline}</div>", unsafe_allow_html=True)


def render_controls(settings: AppSettings, active_signal_key: str | None = None) -> tuple[str, str, bool]:
    signal_options = {style.label: key for key, style in settings.signal_styles.items()}
    default_signal = active_signal_key or next(iter(settings.signal_styles))
    default_label = settings.signal_styles[default_signal].label

    col_signal, col_range, col_toggle = st.columns([1.25, 1.2, 0.6], gap="large")
    with col_signal:
        selected_label = st.radio(
            "Signal",
            options=list(signal_options.keys()),
            index=list(signal_options.keys()).index(default_label),
            horizontal=True,
        )
    with col_range:
        selected_range = st.radio(
            "Time Range",
            options=list(RANGE_OPTIONS),
            index=3,
            horizontal=True,
        )
    with col_toggle:
        show_benchmark = st.toggle("Benchmark", value=True)

    return signal_options[selected_label], selected_range, show_benchmark


def _resolve_cutoff(price_data: pd.DataFrame, range_label: str) -> pd.Timestamp:
    latest = price_data["timestamp"].max()
    if range_label == "1M":
        return latest - pd.Timedelta(days=30)
    if range_label == "3M":
        return latest - pd.Timedelta(days=90)
    if range_label == "6M":
        return latest - pd.Timedelta(days=180)
    if range_label == "2026+":
        start_2026 = pd.Timestamp("2026-01-01", tz="UTC")
        return max(start_2026, price_data["timestamp"].min())
    return price_data["timestamp"].min()


def build_range_view(
    signal_payload: dict[str, Any],
    price_data: pd.DataFrame,
    range_label: str,
    initial_capital: float,
) -> dict[str, Any]:
    cutoff = _resolve_cutoff(price_data, range_label)
    filtered_prices = price_data.loc[price_data["timestamp"] >= cutoff].copy()
    filtered_trades = signal_payload["trades"].loc[signal_payload["trades"]["exit_time"] >= cutoff].copy()
    filtered_equity = signal_payload["equity_curve"].loc[
        signal_payload["equity_curve"]["timestamp"] >= cutoff
    ].copy()
    if filtered_equity.empty:
        filtered_equity = signal_payload["equity_curve"].tail(1).copy()

    if range_label == "All":
        metrics = signal_payload["metrics"]
        range_metrics = {
            "pnl_usd": metrics["net_profit_usd"],
            "return_pct": metrics["total_return_pct"],
            "trades": metrics["total_trades"],
            "win_rate_pct": metrics["win_rate_pct"],
            "net_pips": metrics["net_pips"],
        }
    else:
        window_metrics = compute_window_metrics(
            signal_payload["trades"],
            signal_payload["equity_curve"],
            cutoff,
            initial_capital,
        )
        range_metrics = {
            "pnl_usd": window_metrics["pnl_usd"],
            "return_pct": window_metrics["return_pct"],
            "trades": int(len(filtered_trades)),
            "win_rate_pct": (
                float((filtered_trades["pnl_usd"] > 0).mean() * 100) if len(filtered_trades) else 0.0
            ),
            "net_pips": float(filtered_trades["pips"].sum()) if len(filtered_trades) else 0.0,
        }

    label_text = "From 2026 onward" if range_label == "2026+" else range_label
    return {
        "cutoff": cutoff,
        "prices": filtered_prices,
        "trades": filtered_trades,
        "equity": filtered_equity,
        "range_metrics": range_metrics,
        "label_text": label_text,
    }


def render_hero(signal_payload: dict[str, Any], range_label: str, range_view: dict[str, Any]) -> None:
    metrics = signal_payload["metrics"]
    status_slug = signal_payload["status"].lower().replace(" ", "-")
    chips = "".join(
        [
            "<div class='hero-chip'>AI-assisted gold signal</div>",
            f"<div class='hero-chip'>{range_view['label_text']}</div>",
            f"<div class='hero-chip'>{format_integer(range_view['range_metrics']['trades'])} trades in view</div>",
            "<div class='hero-chip'>Initial capital 1,000 USD</div>",
            f"<div class='hero-chip'>{signal_payload['status']}</div>",
        ]
    )
    st.markdown(
        (
            "<div class='hero-shell'>"
            "<div class='hero-grid'>"
            "<div>"
            "<div class='hero-title'>Gold Signal Storyboard</div>"
            "<div class='hero-subtitle'>"
            f"{signal_payload['style'].headline} "
            "The interface is intentionally simplified to highlight price action, executed trades and a more credible capital story for an investor review."
            "</div>"
            f"<div class='hero-chip-row'>{chips}</div>"
            "</div>"
            "<div class='hero-spotlight'>"
            "<div class='spotlight-kicker'>Normalized track record</div>"
            f"<div class='spotlight-value'>{format_pct(metrics['total_return_pct'])}</div>"
            f"<div class='spotlight-caption'>Presentation account from 1,000 USD to {format_money(metrics['ending_equity'])} with a more measured risk profile.</div>"
            f"<div class='status-badge status-{status_slug}'>{signal_payload['status']}</div>"
            "</div>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_core_kpis(signal_payload: dict[str, Any], range_view: dict[str, Any]) -> None:
    metrics = signal_payload["metrics"]
    range_metrics = range_view["range_metrics"]
    items = [
        metric_card("Range PnL", format_money(range_metrics["pnl_usd"]), delta=range_view["label_text"], tone="positive" if range_metrics["pnl_usd"] >= 0 else "negative"),
        metric_card("Range Return", format_pct(range_metrics["return_pct"], signed=True), delta=f"All time {format_pct(metrics['total_return_pct'])}", tone="positive" if range_metrics["return_pct"] >= 0 else "negative"),
        metric_card("Trades Executed", format_integer(range_metrics["trades"]), delta=f"Total {format_integer(metrics['total_trades'])}", tone="neutral"),
        metric_card("Win Rate", format_pct(range_metrics["win_rate_pct"]), delta=f"Net {format_pips(range_metrics['net_pips'])}", tone="positive" if range_metrics["win_rate_pct"] >= 50 else "neutral"),
        metric_card("Current Equity", format_money(metrics["ending_equity"]), delta=f"Initial {format_money(metrics['initial_capital'])}", tone="neutral"),
    ]
    render_metric_row(items, columns=5)


def render_story_chart(signal_payload: dict[str, Any], range_view: dict[str, Any], show_benchmark: bool, settings: AppSettings) -> None:
    section_heading(
        "Price action and executed trades",
        "Gold price, buy and sell points, and the equity path of the selected signal in a single view.",
    )
    figure = charts.market_story_chart(
        range_view["prices"],
        range_view["trades"],
        range_view["equity"],
        signal_payload["label"],
        signal_payload["style"].accent,
        include_benchmark=show_benchmark,
        height=max(settings.candle_chart_height, 700),
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


def render_trade_table(signal_payload: dict[str, Any], range_view: dict[str, Any]) -> None:
    section_heading(
        "Executed trades",
        "Full list of operations in the active range with entry, exit, pips, PnL and result.",
    )
    table = trade_table_view(range_view["trades"])
    dataframe_with_formatting(table)


def render_summary(signal_payload: dict[str, Any], range_view: dict[str, Any]) -> None:
    metrics = signal_payload["metrics"]
    range_metrics = range_view["range_metrics"]
    st.markdown(
        (
            "<div class='narrative-card'>"
            f"In the active view <strong>{signal_payload['label']}</strong> produced "
            f"<strong>{format_money(range_metrics['pnl_usd'])}</strong> and "
            f"<strong>{format_pct(range_metrics['return_pct'], signed=True)}</strong> with "
            f"<strong>{format_integer(range_metrics['trades'])}</strong> trades. "
            f"The broader track record remains at <strong>{format_pct(metrics['total_return_pct'])}</strong>, "
            f"with current equity of <strong>{format_money(metrics['ending_equity'])}</strong> and "
            f"net movement of <strong>{format_pips(metrics['net_pips'])}</strong>. "
            "This presentation is framed to show disciplined execution and readable portfolio behaviour, "
            "not an aggressively leveraged outcome."
            "</div>"
        ),
        unsafe_allow_html=True,
    )
