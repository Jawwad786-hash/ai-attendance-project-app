import io
import segno
import streamlit as st


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    app_domain = "snapclass-main.streamlit.app"
    join_url = f"{app_domain}/?join-code={subject_code}"

    st.caption(f"Share this link or QR code so students can join **{subject_name}**.")

    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind="png", scale=10, border=1)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("**Join Link**")
        st.code(join_url, language="text")
        st.markdown("**Subject Code**")
        st.code(subject_code, language="text")
        st.info("Copy this link to share via WhatsApp or email.")

    with col2:
        st.markdown("**Scan to Join**")
        st.image(out.getvalue(), caption="QR code for class enrollment", width="stretch")
