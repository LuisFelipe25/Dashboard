from __future__ import annotations

import numpy as np
import pandas as pd

from src.config.settings import AppSettings


def enrich_trade_book(
    trades: pd.DataFrame,
    signal_key: str,
    settings: AppSettings,
) -> pd.DataFrame:
    signal_style = settings.signal_styles[signal_key]
    if trades.empty:
        return pd.DataFrame(
            columns=[
                "signal_key",
                "signal_label",
                "entry_time",
                "exit_time",
                "entry_price",
                "exit_price",
                "pnl_points",
                "pnl_usd",
                "pips",
                "duration",
                "holding_hours",
                "direction",
                "result",
                "trade_index",
                "cum_pnl_usd",
                "cum_pips",
                "outcome_flag",
            ]
        )

    book = trades.copy()
    book["EntryTime"] = pd.to_datetime(book["EntryTime"], utc=True)
    book["ExitTime"] = pd.to_datetime(book["ExitTime"], utc=True)
    book = book.sort_values("ExitTime").reset_index(drop=True)
    book["Duration"] = pd.to_timedelta(book["Duration"])
    book["signal_key"] = signal_key
    book["signal_label"] = signal_style.label
    book["entry_time"] = book["EntryTime"]
    book["exit_time"] = book["ExitTime"]
    book["entry_price"] = book["EntryPrice"].astype(float)
    book["exit_price"] = book["ExitPrice"].astype(float)
    book["pnl_points"] = book["PnL"].astype(float)
    book["pnl_usd"] = book["pnl_points"] * signal_style.scale_factor
    book["pips"] = (book["exit_price"] - book["entry_price"]) * settings.pip_factor
    book["duration"] = book["Duration"]
    book["holding_hours"] = book["duration"].dt.total_seconds() / 3600
    book["direction"] = "Long"
    book["outcome_flag"] = np.sign(book["pnl_usd"]).astype(int)
    book["result"] = np.select(
        [book["pnl_usd"] > 0, book["pnl_usd"] < 0],
        ["Winner", "Loser"],
        default="Flat",
    )
    book["trade_index"] = np.arange(1, len(book) + 1)
    book["cum_pnl_usd"] = book["pnl_usd"].cumsum()
    book["cum_pips"] = book["pips"].cumsum()
    book["signal_executed"] = 1
    book["holding_bucket"] = pd.cut(
        book["holding_hours"],
        bins=[0, 4, 12, 24, 48, np.inf],
        labels=["0-4h", "4-12h", "12-24h", "1-2d", "2d+"],
        include_lowest=True,
    )
    return book


def filter_trades_for_window(trades: pd.DataFrame, cutoff: pd.Timestamp) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    return trades.loc[trades["exit_time"] >= cutoff].copy()


def trade_table_view(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    table = trades.copy()
    table["duration_hours"] = table["holding_hours"].round(1)
    table["open_date"] = table["entry_time"].dt.strftime("%Y-%m-%d %H:%M")
    table["close_date"] = table["exit_time"].dt.strftime("%Y-%m-%d %H:%M")
    return table[
        [
            "open_date",
            "close_date",
            "direction",
            "entry_price",
            "exit_price",
            "pips",
            "pnl_usd",
            "duration_hours",
            "result",
            "signal_label",
        ]
    ].rename(
        columns={
            "open_date": "Open",
            "close_date": "Close",
            "direction": "Type",
            "entry_price": "Entry",
            "exit_price": "Exit",
            "pips": "Pips",
            "pnl_usd": "PnL USD",
            "duration_hours": "Hours",
            "result": "Result",
            "signal_label": "Signal",
        }
    )
