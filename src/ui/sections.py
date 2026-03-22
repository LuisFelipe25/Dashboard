from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.analytics import charts
from src.analytics.trades import filter_trades_for_window, trade_table_view
from src.config.settings import AppSettings
from src.ui.components import (
    dataframe_with_formatting,
    metric_card,
    render_comparison_table,
    render_metric_row,
    render_narrative,
    render_provenance,
    render_recent_trade,
    render_secondary_stats,
    render_window_cards,
    section_heading,
)
from src.ui.formatters import format_duration, format_integer, format_money, format_pct, format_pips, format_ratio


def render_sidebar(dataset: Any, settings: AppSettings, selected_signal_key: str) -> dict[str, Any]:
    with st.sidebar:
        logo_path = settings.assets_dir / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=96)
        st.markdown("### Platform Controls")
        lookback = st.selectbox(
            "Market window",
            options=[30, 60, 90, 120, 180],
            index=3,
            format_func=lambda days: f"Last {days} days",
        )
        show_benchmark = st.toggle("Show benchmark line", value=True)
        st.markdown("---")
        st.markdown("### Data provenance")
        mode_label = (
            settings.artifact_mode_label
            if dataset.provenance.get("real_artifacts_used")
            else "Generated demo fallback"
        )
        render_provenance(dataset.provenance["notes"], mode_label)
        st.markdown("---")
        st.markdown("### Active signal")
        payload = dataset.signals[selected_signal_key]
        st.markdown(f"**{payload['label']}**  \n{payload['style'].description}")
        ml_aux = payload.get("ml_aux_metric")
        if ml_aux:
            st.caption(
                "Métrica ML complementaria: "
                f"{int(ml_aux['blocked_candidates']):,} filtered candidates "
                f"from {int(ml_aux['value']):,} candidate events."
            )
        return {"lookback_days": lookback, "show_benchmark": show_benchmark}


def render_topbar(settings: AppSettings) -> None:
    st.markdown(f"<div class='eyebrow'>{settings.app_tagline}</div>", unsafe_allow_html=True)


def render_signal_selector(settings: AppSettings) -> str:
    options = {style.label: key for key, style in settings.signal_styles.items()}
    selected_label = st.radio(
        "Signal selector",
        options=list(options.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )
    return options[selected_label]


def render_hero(signal_payload: dict[str, Any], dataset: Any, settings: AppSettings) -> None:
    metrics = signal_payload["metrics"]
    style = signal_payload["style"]
    status_slug = signal_payload["status"].lower().replace(" ", "-")
    chips = "".join(
        [
            "<div class='hero-chip'>10,000 USD normalized capital</div>",
            f"<div class='hero-chip'>{signal_payload['label']} active lens</div>",
            f"<div class='hero-chip'>{signal_payload['status']} operating state</div>",
            f"<div class='hero-chip'>{dataset.metadata.get('source_mode', 'demo').replace('_', ' ').title()}</div>",
        ]
    )
    spotlight = (
        "<div class='hero-spotlight'>"
        "<div class='spotlight-kicker'>Highlighted KPI</div>"
        f"<div class='spotlight-value'>{format_pct(metrics['total_return_pct'])}</div>"
        "<div class='spotlight-caption'>Normalized cumulative return from the commercial demo capital profile.</div>"
        f"<div class='status-badge status-{status_slug}'>{signal_payload['status']}</div>"
        "</div>"
    )
    st.markdown(
        (
            "<div class='hero-shell'>"
            "<div class='hero-grid'>"
            "<div>"
            "<div class='hero-title'>Signal Intelligence Platform</div>"
            f"<div class='hero-subtitle'>{style.headline} {settings.app_subtitle}</div>"
            f"<div class='hero-chip-row'>{chips}</div>"
            "</div>"
            f"<div>{spotlight}</div>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_primary_kpis(signal_payload: dict[str, Any]) -> None:
    metrics = signal_payload["metrics"]
    items = [
        metric_card("Initial Capital", format_money(metrics["initial_capital"]), help_text="Portfolio demo baseline."),
        metric_card("Current Equity", format_money(metrics["ending_equity"]), delta=format_money(metrics["net_profit_usd"]), tone="positive" if metrics["net_profit_usd"] >= 0 else "negative", help_text="Live equity projection from the selected signal profile."),
        metric_card("PnL Accumulated", format_money(metrics["net_profit_usd"]), delta=format_pct(metrics["total_return_pct"], signed=True), tone="positive" if metrics["net_profit_usd"] >= 0 else "negative", help_text="Net result on normalized capital."),
        metric_card("Return %", format_pct(metrics["total_return_pct"]), delta=f"Calmar {format_ratio(metrics['calmar_ratio'])}", tone="neutral", help_text="Total return over the loaded sample."),
        metric_card("Sharpe Ratio", format_ratio(metrics["sharpe_ratio"]), delta=f"Sortino {format_ratio(metrics['sortino_ratio'])}", tone="neutral", help_text="Risk-adjusted return quality."),
        metric_card("Max Drawdown", format_pct(metrics["max_drawdown_pct"]), delta=format_money(metrics["max_drawdown_usd"]), tone="negative", help_text="Peak-to-trough equity pressure."),
        metric_card("Win Rate", format_pct(metrics["win_rate_pct"]), delta=f"{format_integer(metrics['winning_trades'])} wins", tone="positive", help_text="Winning trades as a share of total executed positions."),
        metric_card("Total Trades", format_integer(metrics["total_trades"]), delta=f"{format_pips(metrics['net_pips'])}", tone="neutral", help_text="Executed trade count and net pips."),
    ]
    render_metric_row(items, columns=4)


def render_window_section(signal_payload: dict[str, Any]) -> None:
    section_heading(
        "Performance by time window",
        "Recent windows are computed from the active equity profile and recalculated when the global signal changes.",
    )
    render_window_cards(signal_payload["windows"])


def render_equity_section(signal_payload: dict[str, Any], show_benchmark: bool, settings: AppSettings) -> None:
    section_heading(
        "Equity curve",
        "Capital progression from the selected signal, benchmarked against a linear base path from the same initial capital.",
    )
    figure = charts.equity_curve_chart(
        signal_payload["equity_curve"],
        signal_payload["label"],
        signal_payload["style"].accent,
        include_benchmark=show_benchmark,
        height=settings.primary_chart_height,
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


def render_market_section(signal_payload: dict[str, Any], price_data: pd.DataFrame, settings: AppSettings) -> None:
    section_heading(
        "Market structure and executed trades",
        "Candlesticks, entries, exits and trade outcome markers are aligned to the selected XAUUSD market window.",
    )
    trades = filter_trades_for_window(signal_payload["trades"], price_data["timestamp"].min())
    figure = charts.candlestick_trade_chart(
        price_data,
        trades,
        signal_payload["label"],
        signal_payload["style"].accent,
        height=settings.candle_chart_height,
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


def render_trade_analytics(signal_payload: dict[str, Any]) -> None:
    section_heading(
        "Trade distribution and analytics",
        "A compact execution lens across dispersion, win-loss balance, per-trade pips, drawdown pressure and cumulative trade outcome.",
    )
    trades = signal_payload["trades"]
    equity_curve = signal_payload["equity_curve"]
    row_1 = st.columns(2, gap="large")
    row_2 = st.columns(3, gap="large")
    with row_1[0]:
        st.plotly_chart(charts.pnl_distribution_chart(trades), use_container_width=True, config={"displayModeBar": False})
    with row_1[1]:
        st.plotly_chart(charts.win_loss_bar(trades), use_container_width=True, config={"displayModeBar": False})
    with row_2[0]:
        st.plotly_chart(charts.pips_evolution_chart(trades, signal_payload["style"].accent), use_container_width=True, config={"displayModeBar": False})
    with row_2[1]:
        st.plotly_chart(charts.drawdown_timeline_chart(equity_curve), use_container_width=True, config={"displayModeBar": False})
    with row_2[2]:
        st.plotly_chart(charts.cumulative_trade_result_chart(trades, signal_payload["style"].accent), use_container_width=True, config={"displayModeBar": False})


def render_trade_table(signal_payload: dict[str, Any]) -> None:
    section_heading(
        "Trade ledger",
        "Filterable investor-friendly view of executed trades with prices, pips, PnL, duration and outcome.",
    )
    table = trade_table_view(signal_payload["trades"])
    dataframe_with_formatting(table)


def render_narrative_section(signal_payload: dict[str, Any]) -> None:
    section_heading(
        "Executive interpretation",
        "Commercial narrative designed to explain what the selected signal is showing without overselling or relying on ML vanity metrics.",
    )
    left, right = st.columns([1.55, 0.9], gap="large")
    with left:
        render_narrative(signal_payload["narrative"])
    with right:
        render_recent_trade(signal_payload["metrics"])
        st.markdown("<div style='height: 0.75rem'></div>", unsafe_allow_html=True)
        render_secondary_stats(signal_payload["metrics"])


def render_comparison_section(dataset: Any) -> None:
    section_heading(
        "Signal 1 vs Signal 2",
        "Both signals stay visible in the same dashboard so an investor can compare opportunity capture against selectivity and risk efficiency.",
    )
    render_comparison_table(dataset.comparison_table)


def render_footer_notes(signal_payload: dict[str, Any]) -> None:
    metrics = signal_payload["metrics"]
    st.caption(
        "Supplementary execution stats: "
        f"Average trade {format_money(metrics['avg_trade_usd'])}, "
        f"average pips {format_pips(metrics['avg_trade_pips'])}, "
        f"average holding time {format_duration(metrics['avg_holding_time'])}, "
        f"signals executed {format_integer(metrics['signals_executed'])}."
    )
