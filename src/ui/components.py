from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ui.formatters import format_duration, format_integer, format_money, format_pct, format_pips, format_ratio


def section_heading(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def metric_card(title: str, value: str, delta: str | None = None, tone: str = "neutral", help_text: str | None = None) -> str:
    delta_html = f"<div class='metric-delta {tone}'>{delta}</div>" if delta else ""
    help_html = f"<div class='metric-help'>{help_text}</div>" if help_text else ""
    return (
        "<div class='metric-card'>"
        f"<div class='metric-title'>{title}</div>"
        f"<div class='metric-value'>{value}</div>"
        f"{delta_html}"
        f"{help_html}"
        "</div>"
    )


def render_metric_row(items: list[str], columns: int = 4) -> None:
    for start in range(0, len(items), columns):
        cols = st.columns(columns)
        for column, html in zip(cols, items[start : start + columns]):
            with column:
                st.markdown(html, unsafe_allow_html=True)


def render_window_cards(windows: dict[str, dict[str, float]]) -> None:
    cols = st.columns(len(windows))
    for col, (label, data) in zip(cols, windows.items()):
        with col:
            st.markdown(
                (
                    "<div class='window-card'>"
                    f"<div class='window-label'>{label}</div>"
                    f"<div class='window-main'>{format_money(data['pnl_usd'])}</div>"
                    f"<div class='window-line'>Return <span>{format_pct(data['return_pct'], signed=True)}</span></div>"
                    f"<div class='window-line'>Trades <span>{format_integer(data['trades'])}</span></div>"
                    f"<div class='window-line'>Win rate <span>{format_pct(data['win_rate_pct'])}</span></div>"
                    f"<div class='window-line'>Profit factor <span>{format_ratio(data['profit_factor'])}</span></div>"
                    f"<div class='window-line'>Drawdown <span>{format_pct(data['drawdown_pct'])}</span></div>"
                    f"<div class='window-line'>Sharpe <span>{format_ratio(data['sharpe_ratio'])}</span></div>"
                    f"<div class='window-line'>Net pips <span>{format_pips(data['net_pips'])}</span></div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


def render_provenance(notes: list[str], mode_label: str) -> None:
    items = "".join(f"<li>{note}</li>" for note in notes)
    st.markdown(
        (
            "<div class='provenance-card'>"
            f"<div class='provenance-title'>{mode_label}</div>"
            f"<ul>{items}</ul>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_narrative(text: str) -> None:
    st.markdown(f"<div class='narrative-card'>{text}</div>", unsafe_allow_html=True)


def render_comparison_table(comparison_table: pd.DataFrame) -> None:
    cards = []
    for _, row in comparison_table.iterrows():
        cards.append(
            (
                "<div class='comparison-card'>"
                f"<div class='comparison-title'>{row['metric_label']}</div>"
                f"<div class='comparison-row'><span>Signal 1</span><strong>{_comparison_value(row['Signal 1'], row['metric_key'])}</strong></div>"
                f"<div class='comparison-row'><span>Signal 2</span><strong>{_comparison_value(row['Signal 2'], row['metric_key'])}</strong></div>"
                f"<div class='comparison-winner'>Lead: {row['winner']}</div>"
                "</div>"
            )
        )
    render_metric_row(cards, columns=3)


def _comparison_value(value: float, metric_key: str) -> str:
    if metric_key in {"total_return_pct", "max_drawdown_pct", "win_rate_pct"}:
        return format_pct(value, signed=metric_key == "total_return_pct")
    if metric_key == "total_trades":
        return format_integer(value)
    if metric_key == "net_pips":
        return format_pips(value)
    return format_ratio(value)


def dataframe_with_formatting(table: pd.DataFrame) -> None:
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Entry": st.column_config.NumberColumn(format="%.2f"),
            "Exit": st.column_config.NumberColumn(format="%.2f"),
            "Pips": st.column_config.NumberColumn(format="%.0f"),
            "PnL USD": st.column_config.NumberColumn(format="$ %.2f"),
            "Hours": st.column_config.NumberColumn(format="%.1f h"),
        },
    )


def render_recent_trade(metrics: dict[str, object]) -> None:
    recent_time = metrics.get("latest_trade_time")
    recent_time_label = recent_time.strftime("%Y-%m-%d %H:%M UTC") if recent_time is not None else "-"
    html = (
        "<div class='insight-card'>"
        "<div class='insight-title'>Latest operation</div>"
        f"<div class='insight-value'>{recent_time_label}</div>"
        f"<div class='insight-caption'>Result {format_money(float(metrics.get('latest_trade_result', 0.0)))}</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_secondary_stats(metrics: dict[str, object]) -> None:
    html = (
        "<div class='insight-card'>"
        "<div class='insight-title'>Execution profile</div>"
        f"<div class='insight-line'>Expectancy <span>{format_money(float(metrics['expectancy_usd']))}</span></div>"
        f"<div class='insight-line'>Avg duration <span>{format_duration(metrics['avg_holding_time'])}</span></div>"
        f"<div class='insight-line'>Consecutive losses <span>{format_integer(metrics['consecutive_losses_max'])}</span></div>"
        f"<div class='insight-line'>Consecutive wins <span>{format_integer(metrics['consecutive_wins_max'])}</span></div>"
        f"<div class='insight-line'>Best trade <span>{format_money(float(metrics['best_trade_usd']))}</span></div>"
        f"<div class='insight-line'>Worst trade <span>{format_money(float(metrics['worst_trade_usd']))}</span></div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
