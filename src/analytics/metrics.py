from __future__ import annotations

import math
from typing import Any

import pandas as pd

from src.config.settings import AppSettings


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator in (0, 0.0) or pd.isna(denominator):
        return float("nan")
    return float(numerator) / float(denominator)


def _max_streak(mask: pd.Series) -> int:
    if mask.empty:
        return 0
    groups = (~mask).cumsum()
    streaks = mask.groupby(groups).sum()
    return int(streaks.max()) if not streaks.empty else 0


def _daily_returns_from_equity(equity_curve: pd.DataFrame) -> pd.Series:
    if equity_curve.empty:
        return pd.Series(dtype=float)
    daily_equity = (
        equity_curve.set_index("timestamp")["equity"].resample("D").last().ffill()
    )
    return daily_equity.pct_change().dropna()


def _annualized_return(equity_curve: pd.DataFrame, initial_capital: float) -> float:
    if equity_curve.empty:
        return 0.0
    total_days = max((equity_curve["timestamp"].max() - equity_curve["timestamp"].min()).days, 1)
    ending_equity = equity_curve["equity"].iloc[-1]
    growth = max(ending_equity / initial_capital, 1e-9)
    return growth ** (365 / total_days) - 1


def compute_signal_metrics(
    trades: pd.DataFrame,
    equity_curve: pd.DataFrame,
    initial_capital: float,
) -> dict[str, Any]:
    if trades.empty:
        return {
            "initial_capital": initial_capital,
            "ending_equity": initial_capital,
            "total_return_pct": 0.0,
            "net_profit_usd": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "profit_factor": float("nan"),
            "sharpe_ratio": float("nan"),
            "sortino_ratio": float("nan"),
            "calmar_ratio": float("nan"),
            "max_drawdown_pct": 0.0,
            "max_drawdown_usd": 0.0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "breakeven_trades": 0,
            "win_rate_pct": 0.0,
            "avg_trade_usd": 0.0,
            "avg_trade_pips": 0.0,
            "best_trade_usd": 0.0,
            "worst_trade_usd": 0.0,
            "best_trade_pips": 0.0,
            "worst_trade_pips": 0.0,
            "avg_holding_time": pd.Timedelta(0),
            "consecutive_losses_max": 0,
            "consecutive_wins_max": 0,
            "expectancy_usd": 0.0,
            "expectancy_pips": 0.0,
            "net_pips": 0.0,
            "signals_executed": 0,
            "latest_trade_time": None,
            "latest_trade_result": 0.0,
            "monthly_return": 0.0,
            "quarterly_return": 0.0,
            "six_month_return": 0.0,
        }

    pnl = trades["pnl_usd"]
    pips = trades["pips"]
    winners = pnl[pnl > 0]
    losers = pnl[pnl < 0]
    daily_returns = _daily_returns_from_equity(equity_curve)
    downside = daily_returns[daily_returns < 0]
    sharpe_ratio = (
        (daily_returns.mean() / daily_returns.std(ddof=0)) * math.sqrt(252)
        if len(daily_returns) > 1 and daily_returns.std(ddof=0) > 0
        else float("nan")
    )
    sortino_ratio = (
        (daily_returns.mean() / downside.std(ddof=0)) * math.sqrt(252)
        if len(downside) > 1 and downside.std(ddof=0) > 0
        else float("nan")
    )
    max_drawdown_pct = equity_curve["drawdown_pct"].min() if not equity_curve.empty else 0.0
    max_drawdown_usd = equity_curve["drawdown_usd"].min() if not equity_curve.empty else 0.0
    annualized_return = _annualized_return(equity_curve, initial_capital)
    calmar_ratio = _safe_ratio(annualized_return, abs(max_drawdown_pct / 100)) if max_drawdown_pct else float("nan")

    return {
        "initial_capital": initial_capital,
        "ending_equity": float(equity_curve["equity"].iloc[-1]) if not equity_curve.empty else initial_capital,
        "total_return_pct": (
            _safe_ratio(
                float(equity_curve["equity"].iloc[-1]) - initial_capital,
                initial_capital,
            )
            * 100
        )
        if not equity_curve.empty
        else 0.0,
        "net_profit_usd": float(pnl.sum()),
        "gross_profit": float(winners.sum()),
        "gross_loss": abs(float(losers.sum())),
        "profit_factor": _safe_ratio(float(winners.sum()), abs(float(losers.sum()))),
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "calmar_ratio": calmar_ratio,
        "max_drawdown_pct": float(max_drawdown_pct),
        "max_drawdown_usd": abs(float(max_drawdown_usd)),
        "total_trades": int(len(trades)),
        "winning_trades": int((pnl > 0).sum()),
        "losing_trades": int((pnl < 0).sum()),
        "breakeven_trades": int((pnl == 0).sum()),
        "win_rate_pct": _safe_ratio(int((pnl > 0).sum()), len(trades)) * 100,
        "avg_trade_usd": float(pnl.mean()),
        "avg_trade_pips": float(pips.mean()),
        "best_trade_usd": float(pnl.max()),
        "worst_trade_usd": float(pnl.min()),
        "best_trade_pips": float(pips.max()),
        "worst_trade_pips": float(pips.min()),
        "avg_holding_time": trades["duration"].mean(),
        "consecutive_losses_max": _max_streak(pnl < 0),
        "consecutive_wins_max": _max_streak(pnl > 0),
        "expectancy_usd": float(pnl.mean()),
        "expectancy_pips": float(pips.mean()),
        "net_pips": float(pips.sum()),
        "signals_executed": int(trades["signal_executed"].sum()),
        "latest_trade_time": trades["exit_time"].max(),
        "latest_trade_result": float(pnl.iloc[-1]),
    }


def compute_window_metrics(
    trades: pd.DataFrame,
    equity_curve: pd.DataFrame,
    cutoff: pd.Timestamp,
    initial_capital: float,
) -> dict[str, Any]:
    window_trades = trades.loc[trades["exit_time"] >= cutoff].copy()
    if equity_curve.empty:
        return {
            "pnl_usd": 0.0,
            "return_pct": 0.0,
            "trades": 0,
            "win_rate_pct": 0.0,
            "profit_factor": float("nan"),
            "drawdown_pct": 0.0,
            "sharpe_ratio": float("nan"),
            "net_pips": 0.0,
        }

    equity_sorted = equity_curve.sort_values("timestamp")
    start_candidates = equity_sorted.loc[equity_sorted["timestamp"] < cutoff, "equity"]
    start_equity = float(start_candidates.iloc[-1]) if not start_candidates.empty else initial_capital
    end_equity = float(equity_sorted["equity"].iloc[-1])
    window_equity = equity_sorted.loc[equity_sorted["timestamp"] >= cutoff].copy()
    if window_equity.empty:
        window_equity = equity_sorted.tail(1).copy()
    pnl_usd = end_equity - start_equity
    gross_profit = float(window_trades.loc[window_trades["pnl_usd"] > 0, "pnl_usd"].sum())
    gross_loss = abs(float(window_trades.loc[window_trades["pnl_usd"] < 0, "pnl_usd"].sum()))
    daily_returns = _daily_returns_from_equity(window_equity)
    sharpe_ratio = (
        (daily_returns.mean() / daily_returns.std(ddof=0)) * math.sqrt(252)
        if len(daily_returns) > 1 and daily_returns.std(ddof=0) > 0
        else float("nan")
    )
    return {
        "pnl_usd": pnl_usd,
        "return_pct": _safe_ratio(pnl_usd, start_equity) * 100,
        "trades": int(len(window_trades)),
        "win_rate_pct": _safe_ratio(int((window_trades["pnl_usd"] > 0).sum()), len(window_trades)) * 100
        if len(window_trades)
        else 0.0,
        "profit_factor": _safe_ratio(gross_profit, gross_loss),
        "drawdown_pct": float(window_equity["drawdown_pct"].min()) if not window_equity.empty else 0.0,
        "sharpe_ratio": sharpe_ratio,
        "net_pips": float(window_trades["pips"].sum()),
    }


def attach_window_returns(metrics: dict[str, Any], windows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    metrics = metrics.copy()
    metrics["monthly_return"] = windows["1M"]["return_pct"]
    metrics["quarterly_return"] = windows["3M"]["return_pct"]
    metrics["six_month_return"] = windows["6M"]["return_pct"]
    return metrics


def build_comparison_table(
    signal_payloads: dict[str, dict[str, Any]],
    settings: AppSettings,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for metric_key in settings.comparison_metrics:
        values = {
            payload["label"]: payload["metrics"][metric_key]
            for payload in signal_payloads.values()
        }
        higher_is_better = metric_key != "max_drawdown_pct"
        winner = (
            max(values, key=values.get)
            if higher_is_better
            else min(values, key=values.get)
        )
        row = {"metric_key": metric_key, "metric_label": settings.comparison_labels[metric_key], "winner": winner}
        row.update(values)
        rows.append(row)
    return pd.DataFrame(rows)
