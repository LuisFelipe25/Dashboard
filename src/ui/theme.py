from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


def _image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def inject_global_styles(hero_bg_path: Path) -> None:
    hero_bg = _image_data_uri(hero_bg_path)
    st.markdown(
        f"""
        <style>
            :root {{
                --card: rgba(14, 22, 40, 0.78);
                --line: rgba(255,255,255,0.08);
                --text: #EAF0FF;
                --muted: #97A4C0;
                --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
            }}
            .stApp {{
                background:
                    radial-gradient(circle at 12% 10%, rgba(66, 215, 199, 0.12), transparent 26%),
                    radial-gradient(circle at 88% 0%, rgba(247, 185, 85, 0.08), transparent 24%),
                    linear-gradient(180deg, #050914 0%, #09111F 100%);
                color: var(--text);
            }}
            .block-container {{
                max-width: 1440px;
                padding-top: 1.4rem;
                padding-bottom: 4rem;
            }}
            .hero-shell {{
                position: relative;
                overflow: hidden;
                padding: 2rem 2rem 1.8rem;
                border: 1px solid var(--line);
                border-radius: 28px;
                background:
                    linear-gradient(135deg, rgba(12, 22, 42, 0.92), rgba(7, 12, 24, 0.92)),
                    url('{hero_bg}');
                box-shadow: var(--shadow);
                margin-bottom: 1.1rem;
            }}
            .hero-grid {{
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: 1.55fr 0.95fr;
                gap: 1.25rem;
                align-items: stretch;
            }}
            .hero-shell::before {{
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(120deg, rgba(66,215,199,0.12), transparent 30%, rgba(247,185,85,0.08) 100%);
                pointer-events: none;
            }}
            @media (max-width: 980px) {{
                .hero-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            .eyebrow {{
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.45rem 0.75rem;
                font-size: 0.76rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                border-radius: 999px;
                background: rgba(66, 215, 199, 0.12);
                color: #9FF2E5;
                border: 1px solid rgba(66,215,199,0.18);
                margin-bottom: 0.85rem;
            }}
            .hero-title {{
                font-size: clamp(2rem, 4vw, 3.45rem);
                line-height: 1.02;
                font-weight: 700;
                margin-bottom: 0.85rem;
            }}
            .hero-subtitle {{
                font-size: 1.02rem;
                line-height: 1.7;
                color: var(--muted);
                max-width: 56rem;
            }}
            .hero-chip-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.7rem;
                margin-top: 1rem;
            }}
            .hero-chip {{
                padding: 0.7rem 0.9rem;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.08);
                background: rgba(255,255,255,0.035);
                font-size: 0.9rem;
                color: var(--text);
            }}
            .hero-spotlight {{
                border-radius: 24px;
                border: 1px solid rgba(255,255,255,0.08);
                background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.02));
                padding: 1.35rem;
                backdrop-filter: blur(18px);
            }}
            .spotlight-kicker {{
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.72rem;
            }}
            .spotlight-value {{
                font-size: 2.4rem;
                font-weight: 700;
                margin: 0.35rem 0 0.25rem;
            }}
            .spotlight-caption {{
                color: var(--muted);
                font-size: 0.95rem;
            }}
            .status-badge {{
                display: inline-flex;
                margin-top: 0.8rem;
                padding: 0.45rem 0.8rem;
                border-radius: 999px;
                font-weight: 600;
                font-size: 0.8rem;
                border: 1px solid rgba(255,255,255,0.08);
            }}
            .status-active {{ background: rgba(72, 226, 175, 0.12); color: #8CF5CB; }}
            .status-monitored {{ background: rgba(247, 185, 85, 0.12); color: #FFD28B; }}
            .status-historical-demo {{ background: rgba(151, 164, 192, 0.12); color: #C8D2E7; }}
            .section-title {{
                margin-top: 1rem;
                margin-bottom: 0.25rem;
                font-size: 1.15rem;
                font-weight: 700;
                letter-spacing: 0.02em;
            }}
            .section-subtitle {{
                margin-bottom: 1rem;
                color: var(--muted);
                font-size: 0.94rem;
            }}
            .metric-card, .window-card, .comparison-card, .narrative-card, .provenance-card, .insight-card {{
                border: 1px solid var(--line);
                border-radius: 22px;
                background: var(--card);
                box-shadow: var(--shadow);
                backdrop-filter: blur(16px);
            }}
            .metric-card {{
                padding: 1.15rem 1.1rem;
                min-height: 152px;
            }}
            .metric-title {{
                color: var(--muted);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}
            .metric-value {{
                font-size: 2rem;
                font-weight: 700;
                margin-top: 0.45rem;
            }}
            .metric-delta {{
                margin-top: 0.3rem;
                font-size: 0.9rem;
                font-weight: 600;
            }}
            .metric-delta.positive {{ color: #48E2AF; }}
            .metric-delta.negative {{ color: #FF7A8A; }}
            .metric-delta.neutral {{ color: var(--muted); }}
            .metric-help {{
                color: var(--muted);
                margin-top: 0.8rem;
                font-size: 0.84rem;
                line-height: 1.5;
            }}
            .window-card {{
                padding: 1.2rem;
                min-height: 245px;
            }}
            .window-label {{
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--muted);
            }}
            .window-main {{
                font-size: 1.9rem;
                font-weight: 700;
                margin: 0.55rem 0 0.7rem;
            }}
            .window-line {{
                display: flex;
                justify-content: space-between;
                gap: 0.75rem;
                padding: 0.18rem 0;
                font-size: 0.9rem;
                color: var(--muted);
            }}
            .window-line span {{
                color: var(--text);
                font-weight: 600;
            }}
            .comparison-card {{
                padding: 1rem 1rem 0.9rem;
                min-height: 168px;
            }}
            .comparison-title {{
                font-size: 0.9rem;
                color: var(--muted);
                margin-bottom: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}
            .comparison-row {{
                display: flex;
                justify-content: space-between;
                gap: 0.75rem;
                padding: 0.18rem 0;
            }}
            .comparison-winner {{
                margin-top: 0.65rem;
                color: #A7F3E7;
                font-size: 0.86rem;
            }}
            .narrative-card {{
                padding: 1.25rem 1.3rem;
                line-height: 1.75;
                color: #D6DEF1;
            }}
            .provenance-card {{
                padding: 1rem 1.1rem;
            }}
            .provenance-title {{
                font-size: 0.84rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #9FF2E5;
                margin-bottom: 0.65rem;
            }}
            .provenance-card ul {{
                margin: 0;
                padding-left: 1.1rem;
                color: var(--muted);
            }}
            .insight-card {{
                padding: 1rem 1.1rem;
                min-height: 155px;
            }}
            .insight-title {{
                color: var(--muted);
                text-transform: uppercase;
                font-size: 0.78rem;
                letter-spacing: 0.08em;
                margin-bottom: 0.55rem;
            }}
            .insight-value {{
                font-size: 1.25rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }}
            .insight-caption, .insight-line {{
                color: var(--muted);
                font-size: 0.9rem;
            }}
            .insight-line {{
                display: flex;
                justify-content: space-between;
                gap: 0.75rem;
                padding: 0.14rem 0;
            }}
            .insight-line span {{
                color: var(--text);
                font-weight: 600;
            }}
            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, rgba(8,14,28,0.92), rgba(6,10,20,0.98));
                border-right: 1px solid rgba(255,255,255,0.06);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
