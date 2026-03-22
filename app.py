from __future__ import annotations

import streamlit as st

from src.config.settings import get_app_settings
from src.data.loader import load_dashboard_dataset
from src.ui.sections import (
    build_range_view,
    render_controls,
    render_hero,
    render_core_kpis,
    render_story_chart,
    render_summary,
    render_topbar,
    render_trade_table,
)
from src.ui.theme import inject_global_styles


def main() -> None:
    settings = get_app_settings()
    st.set_page_config(
        page_title=settings.app_name,
        page_icon="chart_with_upwards_trend",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_global_styles(settings.assets_dir / "hero_bg.png")
    dataset = load_dashboard_dataset(settings)

    render_topbar(settings)
    selected_signal_key, selected_range, show_benchmark = render_controls(settings)
    signal_payload = dataset.signals[selected_signal_key]
    range_view = build_range_view(
        signal_payload,
        dataset.price_data,
        selected_range,
        settings.initial_capital,
    )

    render_hero(signal_payload, selected_range, range_view)
    render_core_kpis(signal_payload, range_view)
    render_story_chart(signal_payload, range_view, show_benchmark, settings)
    render_summary(signal_payload, range_view)
    render_trade_table(signal_payload, range_view)


if __name__ == "__main__":
    main()
