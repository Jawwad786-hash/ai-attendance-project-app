import streamlit as st
from src.database.db import create_attendance


def show_attendance_result(df, logs):
    st.caption("Please review the detected attendance before saving to records.")
    st.dataframe(df, hide_index=True, width="stretch")

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="small")

    with col1:
        if st.button("Discard", type="secondary", width="stretch"):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button("Confirm & Save", width="stretch", type="primary"):
            try:
                create_attendance(logs)
                st.toast("Attendance saved!")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception:
                st.error("Sync failed! Please try again.")


@st.dialog("Attendance Report")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)
