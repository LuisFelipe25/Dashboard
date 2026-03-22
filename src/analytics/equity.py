from __future__ import annotations

import numpy as np
import pandas as pd


def build_equity_curve(
    trades: pd.DataFrame,
    price_data: pd.DataFrame,
    initial_capital: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if price_data.empty:
        return pd.DataFrame(), trades.copy()

    trade_book = trades.sort_values("exit_time").copy()
    price_frame = price_data[["timestamp"]].drop_duplicates().sort_values("timestamp").copy()

    if trade_book.empty:
        price_frame["equity"] = initial_capital
        price_frame["benchmark"] = initial_capital
        price_frame["drawdown_pct"] = 0.0
        price_frame["drawdown_usd"] = 0.0
        return price_frame, trade_book

    trade_book["equity_before_trade"] = initial_capital + trade_book["pnl_usd"].cumsum() - trade_book["pnl_usd"]
    trade_book["equity_after_trade"] = trade_book["equity_before_trade"] + trade_book["pnl_usd"]
    trade_book["portfolio_return_pct"] = (
        trade_book["pnl_usd"] / trade_book["equity_before_trade"].replace(0, np.nan)
    ) * 100

    equity_points = pd.concat(
        [
            pd.DataFrame(
                {"timestamp": [price_frame["timestamp"].min()], "equity": [initial_capital]}
            ),
            trade_book[["exit_time", "equity_after_trade"]].rename(
                columns={"exit_time": "timestamp", "equity_after_trade": "equity"}
            ),
        ],
        ignore_index=True,
    ).sort_values("timestamp")

    curve = pd.merge_asof(
        price_frame,
        equity_points,
        on="timestamp",
        direction="backward",
    )
    curve["equity"] = curve["equity"].fillna(initial_capital)
    curve["peak_equity"] = curve["equity"].cummax()
    curve["drawdown_usd"] = curve["equity"] - curve["peak_equity"]
    curve["drawdown_pct"] = np.where(
        curve["peak_equity"] > 0,
        (curve["equity"] / curve["peak_equity"] - 1.0) * 100,
        0.0,
    )
    curve["benchmark"] = np.linspace(initial_capital, curve["equity"].iloc[-1], len(curve))
    curve["date"] = curve["timestamp"].dt.floor("D")
    return curve, trade_book


def window_equity_slice(equity_curve: pd.DataFrame, cutoff: pd.Timestamp) -> pd.DataFrame:
    if equity_curve.empty:
        return equity_curve.copy()
    return equity_curve.loc[equity_curve["timestamp"] >= cutoff].copy()
