import streamlit as st
from src.components.header import header_home
from src.ui.base_layout import style_background_home, style_base_layout


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(key="snap_card_student_portal", border=True):
            st.markdown(
                """
                <div style="text-align:center;">
                    <div class="snap-avatar-badge">
                        <img src="https://i.ibb.co/844D9Lrt/mascot-student.png" alt="Student portal" />
                    </div>
                    <h2 style="margin:0 0 0.35rem; color:#0F172A;">Student Portal</h2>
                    <p class="snap-subtitle" style="color:#475569;">
                        Instant biometric sign-in and personal attendance tracking.
                    </p>
                    <ul class="snap-feature-list">
                        <li><span class="snap-feature-dot"></span>Sign in effortlessly with FaceID</li>
                        <li><span class="snap-feature-dot"></span>Join classes via code or QR link</li>
                        <li><span class="snap-feature-dot"></span>Monitor attendance across subjects</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "Enter Student Portal",
                type="primary",
                icon=":material/arrow_outward:",
                icon_position="right",
                width="stretch",
            ):
                st.session_state["login_type"] = "student"
                st.rerun()

    with col2:
        with st.container(key="snap_card_teacher_portal", border=True):
            st.markdown(
                """
                <div style="text-align:center;">
                    <div class="snap-avatar-badge">
                        <img src="https://i.ibb.co/CsmQQV6X/mascot-prof.png" alt="Teacher portal" />
                    </div>
                    <h2 style="margin:0 0 0.35rem; color:#0F172A;">Teacher Portal</h2>
                    <p class="snap-subtitle" style="color:#475569;">
                        Automated roll call using classroom photos and voice audio.
                    </p>
                    <ul class="snap-feature-list">
                        <li><span class="snap-feature-dot"></span>Scan multi-photo classroom snapshots</li>
                        <li><span class="snap-feature-dot"></span>Run voice-based speaker attendance</li>
                        <li><span class="snap-feature-dot"></span>Share join QR codes &amp; review logs</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "Enter Teacher Portal",
                type="primary",
                icon=":material/arrow_outward:",
                icon_position="right",
                width="stretch",
            ):
                st.session_state["login_type"] = "teacher"
                st.rerun()
