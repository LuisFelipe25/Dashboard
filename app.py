from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config.settings import get_app_settings
from src.data.loader import load_dashboard_dataset
from src.ui.sections import (
    render_comparison_section,
    render_equity_section,
    render_footer_notes,
    render_hero,
    render_market_section,
    render_narrative_section,
    render_primary_kpis,
    render_signal_selector,
    render_sidebar,
    render_topbar,
    render_trade_analytics,
    render_trade_table,
    render_window_section,
)
from src.ui.theme import inject_global_styles


def main() -> None:
    settings = get_app_settings()
    st.set_page_config(
        page_title=settings.app_name,
        page_icon="chart_with_upwards_trend",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_global_styles(settings.assets_dir / "hero_bg.png")
    dataset = load_dashboard_dataset(settings)

    render_topbar(settings)
    selected_signal_key = render_signal_selector(settings)
    render_hero(dataset.signals[selected_signal_key], dataset, settings)

    controls = render_sidebar(dataset, settings, selected_signal_key)
    signal_payload = dataset.signals[selected_signal_key]
    latest_time = dataset.price_data["timestamp"].max()
    chart_cutoff = latest_time - pd.Timedelta(days=controls["lookback_days"])
    chart_prices = dataset.price_data.loc[dataset.price_data["timestamp"] >= chart_cutoff].copy()

    render_primary_kpis(signal_payload)
    render_window_section(signal_payload)
    render_equity_section(signal_payload, controls["show_benchmark"], settings)
    render_market_section(signal_payload, chart_prices, settings)
    render_trade_analytics(signal_payload)
    render_trade_table(signal_payload)
    render_narrative_section(signal_payload)
    render_comparison_section(dataset)
    render_footer_notes(signal_payload)


if __name__ == "__main__":
    main()
