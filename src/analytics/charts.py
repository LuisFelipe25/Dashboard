from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _base_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(9, 14, 28, 0.65)",
        font=dict(color="#E8EEF9", family="Trebuchet MS, Segoe UI, sans-serif"),
        hoverlabel=dict(bgcolor="#121A2E", font_color="#E8EEF9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=False),
    )
    return fig


def equity_curve_chart(
    equity_curve: pd.DataFrame,
    signal_label: str,
    accent: str,
    include_benchmark: bool = True,
    height: int = 420,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=equity_curve["timestamp"],
            y=equity_curve["equity"],
            mode="lines",
            name=f"{signal_label} Equity",
            line=dict(color=accent, width=3),
        )
    )
    if include_benchmark:
        fig.add_trace(
            go.Scatter(
                x=equity_curve["timestamp"],
                y=equity_curve["benchmark"],
                mode="lines",
                name="Linear benchmark",
                line=dict(color="#9AA6BF", width=1.4, dash="dot"),
            )
        )
    fig.update_yaxes(title="Equity (USD)")
    return _base_layout(fig, height)


def market_story_chart(
    prices: pd.DataFrame,
    trades: pd.DataFrame,
    equity_curve: pd.DataFrame,
    signal_label: str,
    accent: str,
    include_benchmark: bool = True,
    height: int = 700,
) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.62, 0.38],
    )
    fig.add_trace(
        go.Scatter(
            x=prices["timestamp"],
            y=prices["close"],
            mode="lines",
            name="Gold price",
            line=dict(color="#E7EEF8", width=2.6, shape="spline", smoothing=1.05),
            fill="tozeroy",
            fillcolor="rgba(231, 238, 248, 0.05)",
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Gold: %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=trades["entry_time"],
            y=trades["entry_price"],
            mode="markers",
            name="Buy",
            marker=dict(color=accent, size=10, symbol="triangle-up", line=dict(color="#081018", width=1)),
            hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>Buy: %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=trades["exit_time"],
            y=trades["exit_price"],
            mode="markers",
            name="Sell",
            marker=dict(
                color=np.where(trades["pnl_usd"] >= 0, "#41E1B7", "#FF7A8A"),
                size=9,
                symbol="circle",
                line=dict(color="#081018", width=1),
            ),
            customdata=np.c_[trades["pnl_usd"], trades["pips"]],
            hovertemplate=(
                "<b>%{x|%Y-%m-%d %H:%M}</b><br>"
                "Sell: %{y:.2f}<br>"
                "PnL: %{customdata[0]:.2f} USD<br>"
                "Pips: %{customdata[1]:.0f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=equity_curve["timestamp"],
            y=equity_curve["equity"],
            mode="lines",
            name=f"{signal_label} equity",
            line=dict(color=accent, width=3, shape="spline", smoothing=0.95),
            fill="tozeroy",
            fillcolor="rgba(66, 215, 199, 0.10)",
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Equity: %{y:.2f} USD<extra></extra>",
        ),
        row=2,
        col=1,
    )
    if include_benchmark:
        fig.add_trace(
            go.Scatter(
                x=equity_curve["timestamp"],
                y=equity_curve["benchmark"],
                mode="lines",
                name="Benchmark",
                line=dict(color="#F7B955", width=1.8, dash="dot"),
                hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Benchmark: %{y:.2f} USD<extra></extra>",
            ),
            row=2,
            col=1,
        )
    fig.update_yaxes(title="Gold", row=1, col=1)
    fig.update_yaxes(title="Equity", row=2, col=1)
    fig.update_layout(hovermode="x unified", transition_duration=350)
    return _base_layout(fig, height)


def candlestick_trade_chart(
    prices: pd.DataFrame,
    trades: pd.DataFrame,
    signal_label: str,
    accent: str,
    height: int = 620,
) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.74, 0.26])
    fig.add_trace(
        go.Candlestick(
            x=prices["timestamp"],
            open=prices["open"],
            high=prices["high"],
            low=prices["low"],
            close=prices["close"],
            name="XAUUSD",
            increasing_line_color="#44E2AE",
            decreasing_line_color="#FF6B77",
            increasing_fillcolor="#44E2AE",
            decreasing_fillcolor="#FF6B77",
        ),
        row=1,
        col=1,
    )

    winners = trades[trades["pnl_usd"] > 0]
    losers = trades[trades["pnl_usd"] < 0]
    for dataset, color, name, symbol in (
        (winners, "#4EF0C0", "Winning exits", "diamond"),
        (losers, "#FF7A8A", "Losing exits", "x"),
    ):
        fig.add_trace(
            go.Scatter(
                x=dataset["exit_time"],
                y=dataset["exit_price"],
                mode="markers",
                name=name,
                marker=dict(color=color, size=9, symbol=symbol, line=dict(width=1, color="#0A1020")),
                hovertemplate=(
                    "<b>%{x|%Y-%m-%d %H:%M}</b><br>"
                    f"{signal_label}<br>"
                    "Exit: %{y:.2f}<br>"
                    "PnL: %{customdata[0]:.2f} USD<br>"
                    "Pips: %{customdata[1]:.0f}<extra></extra>"
                ),
                customdata=np.c_[dataset["pnl_usd"], dataset["pips"]],
            ),
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=trades["entry_time"],
            y=trades["entry_price"],
            mode="markers",
            name="Entries",
            marker=dict(color=accent, size=7, symbol="triangle-up", line=dict(width=1, color="#081018")),
            hovertemplate=(
                "<b>%{x|%Y-%m-%d %H:%M}</b><br>"
                "Entry: %{y:.2f}<br>"
                "Signal: %{customdata[0]}<extra></extra>"
            ),
            customdata=np.c_[trades["signal_label"]],
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=trades["exit_time"],
            y=trades["pnl_usd"],
            name="Trade PnL",
            marker_color=np.where(trades["pnl_usd"] >= 0, "#35DFA7", "#FF7A8A"),
            hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>PnL: %{y:.2f} USD<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_yaxes(title="Price", row=1, col=1)
    fig.update_yaxes(title="PnL USD", row=2, col=1, gridcolor="rgba(255,255,255,0.08)")
    return _base_layout(fig, height)


def pnl_distribution_chart(trades: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        trades,
        x="pnl_usd",
        nbins=28,
        color_discrete_sequence=["#49D8C8"],
        opacity=0.82,
    )
    fig.update_xaxes(title="PnL per trade (USD)")
    fig.update_yaxes(title="Trades")
    return _base_layout(fig, 300)


def win_loss_bar(trades: pd.DataFrame) -> go.Figure:
    counts = pd.DataFrame(
        {
            "Result": ["Winners", "Losers", "Flat"],
            "Count": [
                int((trades["pnl_usd"] > 0).sum()),
                int((trades["pnl_usd"] < 0).sum()),
                int((trades["pnl_usd"] == 0).sum()),
            ],
        }
    )
    fig = px.bar(
        counts,
        x="Result",
        y="Count",
        color="Result",
        color_discrete_map={"Winners": "#41E1B7", "Losers": "#FF7A8A", "Flat": "#7F8BA3"},
    )
    return _base_layout(fig, 300)


def pips_evolution_chart(trades: pd.DataFrame, accent: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trades["trade_index"],
            y=trades["pips"],
            mode="lines+markers",
            name="Pips / trade",
            line=dict(color=accent, width=2),
            marker=dict(size=5),
        )
    )
    fig.update_xaxes(title="Trade index")
    fig.update_yaxes(title="Pips")
    return _base_layout(fig, 300)


def drawdown_timeline_chart(equity_curve: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=equity_curve["timestamp"],
            y=equity_curve["drawdown_pct"],
            mode="lines",
            fill="tozeroy",
            line=dict(color="#FF7A8A", width=2),
            fillcolor="rgba(255, 122, 138, 0.18)",
            name="Drawdown",
        )
    )
    fig.update_yaxes(title="Drawdown %")
    return _base_layout(fig, 300)


def cumulative_trade_result_chart(trades: pd.DataFrame, accent: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trades["trade_index"],
            y=trades["cum_pnl_usd"],
            mode="lines",
            line=dict(color=accent, width=3),
            name="Cumulative PnL",
        )
    )
    fig.update_xaxes(title="Trade index")
    fig.update_yaxes(title="Cum. PnL USD")
    return _base_layout(fig, 300)
