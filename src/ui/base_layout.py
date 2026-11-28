import streamlit as st


def style_background_home():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #1E2552 !important;
                background-image:
                    radial-gradient(ellipse 85% 50% at 50% -5%, rgba(129, 140, 248, 0.28), transparent 68%),
                    radial-gradient(ellipse 60% 45% at 85% 95%, rgba(79, 70, 229, 0.18), transparent 65%),
                    radial-gradient(rgba(255, 255, 255, 0.09) 1px, transparent 1px) !important;
                background-size: 100% 100%, 100% 100%, 26px 26px !important;
            }

            [class*="st-key-snap_card_"] {
                background-color: #FFFFFF !important;
                border: 1px solid rgba(226, 232, 240, 0.95) !important;
                border-radius: 1.5rem !important;
                padding: 2rem 1.75rem !important;
                box-shadow: 0 22px 48px rgba(10, 14, 38, 0.30) !important;
                transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.24s ease, border-color 0.24s ease !important;
                animation: snapFadeUp 0.48s cubic-bezier(0.22, 1, 0.36, 1) both;
            }

            [class*="st-key-snap_card_teacher"] {
                animation-delay: 0.08s;
            }

            [class*="st-key-snap_card_"]:hover {
                transform: translateY(-5px) !important;
                box-shadow: 0 30px 60px rgba(10, 14, 38, 0.38) !important;
                border-color: #C7D2FE !important;
            }

            [class*="st-key-snap_card_"]:hover .snap-avatar-badge {
                transform: scale(1.06);
                background: #E0E7FF;
            }

            [class*="st-key-snap_card_"] h2,
            [class*="st-key-snap_card_"] h3,
            [class*="st-key-snap_card_"] li {
                color: #0F172A !important;
            }

            [class*="st-key-snap_card_"] .snap-subtitle {
                color: #475569 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_background_dashboard():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #F4F6FB !important;
                background-image:
                    radial-gradient(ellipse 90% 40% at 50% 0%, rgba(79, 70, 229, 0.06), transparent 65%),
                    linear-gradient(to right, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(148, 163, 184, 0.08) 1px, transparent 1px) !important;
                background-size: 100% 100%, 32px 32px, 32px 32px !important;
            }

            [class*="st-key-snap_card_"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 1.15rem !important;
                padding: 1.4rem 1.5rem !important;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.04) !important;
                animation: snapFadeUp 0.38s cubic-bezier(0.22, 1, 0.36, 1) both;
            }

            [class*="st-key-snap_tabbar"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 1rem !important;
                padding: 0.4rem !important;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
                animation: snapFadeUp 0.32s cubic-bezier(0.22, 1, 0.36, 1) both;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_base_layout():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            @keyframes snapFadeUp {
                from {
                    opacity: 0;
                    transform: translateY(12px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            #MainMenu,
            footer,
            header[data-testid="stHeader"],
            [data-testid="stToolbar"],
            [data-testid="stDecoration"] {
                display: none !important;
                visibility: hidden !important;
            }

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                color: #0F172A;
            }

            .block-container {
                max-width: 1100px !important;
                padding-top: 1.6rem !important;
                padding-bottom: 3rem !important;
                padding-left: 1.5rem !important;
                padding-right: 1.5rem !important;
            }

            h1, h2, h3, h4 {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
                letter-spacing: -0.025em;
                color: #0F172A;
            }

            h1 {
                font-size: 2.05rem !important;
                font-weight: 800 !important;
                line-height: 1.15 !important;
                margin-bottom: 0.2rem !important;
            }

            h2 {
                font-size: 1.45rem !important;
                font-weight: 700 !important;
                line-height: 1.25 !important;
                margin-bottom: 0.2rem !important;
            }

            h3 {
                font-size: 1.1rem !important;
                font-weight: 700 !important;
            }

            p, label, span {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            .snapclass-wordmark {
                font-family: 'Climate Crisis', sans-serif !important;
                letter-spacing: 0.02em;
                line-height: 1.02 !important;
            }

            .snap-hero {
                animation: snapFadeUp 0.42s cubic-bezier(0.22, 1, 0.36, 1) both;
            }

            .snap-eyebrow {
                display: inline-block;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                padding: 0.32rem 0.8rem;
                border-radius: 999px;
                margin-bottom: 0.85rem;
            }

            .snap-eyebrow-dark {
                background: rgba(129, 140, 248, 0.18);
                color: #E0E7FF;
                border: 1px solid rgba(165, 180, 252, 0.32);
            }

            .snap-eyebrow-light {
                background: #EEF2FF;
                color: #4338CA;
                border: 1px solid #C7D2FE;
            }

            .snap-subtitle {
                color: #475569;
                font-size: 0.95rem;
                line-height: 1.55;
                margin: 0.2rem 0 0;
            }

            .snap-avatar-badge {
                width: 88px;
                height: 88px;
                border-radius: 50%;
                background: #EEF2FF;
                border: 1px solid #E0E7FF;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 0.95rem;
                transition: transform 0.22s ease, background-color 0.22s ease;
            }

            .snap-avatar-badge img {
                height: 58px;
                width: 58px;
                object-fit: contain;
            }

            .snap-feature-list {
                list-style: none;
                padding: 0;
                margin: 1rem 0 1.3rem;
                text-align: left;
            }

            .snap-feature-list li {
                font-size: 0.89rem;
                color: #334155;
                padding: 0.3rem 0;
                display: flex;
                align-items: center;
                gap: 0.55rem;
            }

            .snap-feature-dot {
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: #4F46E5;
                flex-shrink: 0;
            }

            .snap-user-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                background: #FFFFFF;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                padding: 0.44rem 0.95rem;
                border-radius: 999px;
                font-size: 0.88rem;
                font-weight: 600;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            }

            .snap-stat-box {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 0.95rem;
                padding: 1rem 1.15rem;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
                animation: snapFadeUp 0.38s cubic-bezier(0.22, 1, 0.36, 1) both;
                transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
            }

            .snap-stat-box:hover {
                transform: translateY(-2px);
                border-color: #CBD5E1;
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
            }

            .snap-stat-label {
                font-size: 0.74rem;
                font-weight: 700;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }

            .snap-stat-value {
                font-size: 1.55rem;
                font-weight: 800;
                color: #0F172A;
                font-variant-numeric: tabular-nums;
                margin-top: 0.2rem;
            }

            .snap-subject-card {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-left: 4px solid #4F46E5;
                border-radius: 1rem;
                padding: 1.3rem 1.35rem;
                margin-bottom: 0.65rem;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
                animation: snapFadeUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
                transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s ease, border-color 0.2s ease;
            }

            .snap-subject-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 26px rgba(15, 23, 42, 0.08);
                border-color: #CBD5E1;
                border-left-color: #4338CA;
            }

            .snap-subject-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 0.75rem;
                flex-wrap: wrap;
            }

            .snap-subject-title {
                margin: 0;
                color: #0F172A;
                font-size: 1.16rem;
                font-weight: 700;
                line-height: 1.3;
            }

            .snap-code-pill {
                background: #EEF2FF;
                color: #4338CA;
                border: 1px solid #C7D2FE;
                padding: 2px 10px;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.02em;
            }

            .snap-subject-section {
                color: #64748B;
                margin: 0.35rem 0 0.85rem;
                font-size: 0.88rem;
                font-weight: 500;
            }

            .snap-chips-row {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .snap-chip {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                color: #334155;
                padding: 0.32rem 0.72rem;
                border-radius: 0.6rem;
                font-size: 0.84rem;
                font-weight: 500;
                font-variant-numeric: tabular-nums;
            }

            .snap-progress-wrap {
                margin-top: 0.85rem;
            }

            .snap-progress-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.78rem;
                font-weight: 600;
                color: #475569;
                margin-bottom: 0.3rem;
            }

            .snap-progress-track {
                height: 6px;
                width: 100%;
                background: #E2E8F0;
                border-radius: 999px;
                overflow: hidden;
            }

            .snap-progress-fill {
                height: 100%;
                background: #4F46E5;
                border-radius: 999px;
                transition: width 0.45s cubic-bezier(0.22, 1, 0.36, 1);
            }

            button[kind="primary"],
            button[data-testid="stBaseButton-primary"],
            button[kind="secondary"],
            button[data-testid="stBaseButton-secondary"],
            button[kind="tertiary"],
            button[data-testid="stBaseButton-tertiary"] {
                border-radius: 0.85rem !important;
                font-weight: 600 !important;
                font-size: 0.92rem !important;
                min-height: 2.7rem !important;
                padding: 0.5rem 1.15rem !important;
                transition: background-color 0.16s ease, border-color 0.16s ease, color 0.16s ease, transform 0.16s ease, box-shadow 0.16s ease !important;
            }

            button[kind="primary"],
            button[data-testid="stBaseButton-primary"] {
                background-color: #4F46E5 !important;
                color: #FFFFFF !important;
                border: 1px solid #4F46E5 !important;
                box-shadow: 0 2px 8px rgba(79, 70, 229, 0.22) !important;
            }

            button[kind="primary"]:hover:not(:disabled),
            button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
                background-color: #4338CA !important;
                border-color: #4338CA !important;
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(79, 70, 229, 0.30) !important;
            }

            button[kind="secondary"],
            button[data-testid="stBaseButton-secondary"] {
                background-color: #FFFFFF !important;
                color: #0F172A !important;
                border: 1px solid #CBD5E1 !important;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
            }

            button[kind="secondary"]:hover:not(:disabled),
            button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {
                background-color: #F8FAFC !important;
                border-color: #94A3B8 !important;
                transform: translateY(-1px);
            }

            button[kind="tertiary"],
            button[data-testid="stBaseButton-tertiary"] {
                background-color: #FFFFFF !important;
                color: #475569 !important;
                border: 1px solid #E2E8F0 !important;
            }

            button[kind="tertiary"]:hover:not(:disabled),
            button[data-testid="stBaseButton-tertiary"]:hover:not(:disabled) {
                background-color: #EEF2FF !important;
                color: #3730A3 !important;
                border-color: #C7D2FE !important;
                transform: translateY(-1px);
            }

            button:disabled {
                opacity: 0.42 !important;
                cursor: not-allowed !important;
                transform: none !important;
                box-shadow: none !important;
            }

            button:focus-visible,
            input:focus-visible,
            [tabindex]:focus-visible {
                outline: 2px solid #4F46E5 !important;
                outline-offset: 2px !important;
            }

            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div {
                border-radius: 0.75rem !important;
                border-color: #CBD5E1 !important;
                background-color: #FFFFFF !important;
            }

            [data-testid="stCameraInput"] > div,
            [data-testid="stFileUploaderDropzone"] {
                border-radius: 1rem !important;
                border-color: #CBD5E1 !important;
                background-color: #F8FAFC !important;
            }

            [data-testid="stDataFrame"] {
                border: 1px solid #E2E8F0 !important;
                border-radius: 0.95rem !important;
                overflow: hidden !important;
                background: #FFFFFF !important;
            }

            [data-testid="stDialog"] div[role="dialog"] {
                border-radius: 1.25rem !important;
                border: 1px solid #E2E8F0 !important;
            }

            hr {
                border-color: #E2E8F0 !important;
                margin: 1.2rem 0 !important;
            }

            @media (max-width: 768px) {
                .block-container {
                    padding-top: 1rem !important;
                    padding-left: 0.85rem !important;
                    padding-right: 0.85rem !important;
                }

                h1 {
                    font-size: 1.65rem !important;
                }

                h2 {
                    font-size: 1.25rem !important;
                }
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    transition: none !important;
                    animation: none !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
