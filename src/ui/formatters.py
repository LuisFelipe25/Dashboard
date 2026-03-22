from __future__ import annotations

import math
from datetime import timedelta


def format_money(value: float, compact: bool = False) -> str:
    if value is None or math.isnan(value):
        return "-"
    if compact and abs(value) >= 1_000:
        suffixes = [(1_000_000, "M"), (1_000, "K")]
        for divider, suffix in suffixes:
            if abs(value) >= divider:
                return f"${value / divider:,.2f}{suffix}"
    return f"${value:,.2f}"


def format_pct(value: float, decimals: int = 2, signed: bool = False) -> str:
    if value is None or math.isnan(value):
        return "-"
    sign = "+" if signed and value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def format_ratio(value: float, decimals: int = 2) -> str:
    if value is None or math.isnan(value):
        return "-"
    return f"{value:.{decimals}f}"


def format_integer(value: float | int) -> str:
    if value is None:
        return "-"
    return f"{int(round(value)):,}"


def format_pips(value: float, decimals: int = 0) -> str:
    if value is None or math.isnan(value):
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f} pips"


def format_duration(value: timedelta | float | int | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, (float, int)):
        value = timedelta(hours=float(value))
    total_hours = int(value.total_seconds() // 3600)
    days, hours = divmod(total_hours, 24)
    if days and hours:
        return f"{days}d {hours}h"
    if days:
        return f"{days}d"
    return f"{hours}h"
