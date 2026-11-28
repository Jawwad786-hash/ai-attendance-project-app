import streamlit as st


def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(
        f"""
        <div class="snap-hero" style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin:0.65rem 0 2rem; text-align:center;">
            <span class="snap-eyebrow snap-eyebrow-dark">AI Classroom Attendance</span>
            <div style="display:flex; align-items:center; justify-content:center; gap:0.9rem; flex-wrap:wrap;">
                <img src="{logo_url}" alt="SnapClass logo" style="height:64px;" />
                <div class="snapclass-wordmark" style="font-size:clamp(2.1rem, 4.5vw, 3rem); color:#FFFFFF; text-align:left;">
                    SNAP<br/>CLASS
                </div>
            </div>
            <p style="color:#E2E8F0; font-size:1.02rem; line-height:1.55; margin:0.95rem 0 0; max-width:480px;">
                Fast, contactless attendance powered by face recognition and classroom voice detection.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:flex-start; gap:0.75rem;">
            <img src="{logo_url}" alt="SnapClass logo" style="height:48px;" />
            <div>
                <h2 class="snapclass-wordmark" style="font-size:1.3rem !important; color:#4F46E5 !important; margin:0 !important;">
                    SNAP<br/>CLASS
                </h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
