import streamlit as st
from PIL import Image


@st.dialog("Capture or Upload Photos")
def add_photos_dialog():
    st.caption("Add one or more classroom photos to scan for student attendance.")

    if "photo_tab" not in st.session_state:
        st.session_state.photo_tab = "camera"

    t1, t2 = st.columns(2, gap="small")

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == "camera" else "tertiary"
        if st.button("Camera", type=type_camera, icon=":material/photo_camera:", width="stretch"):
            st.session_state.photo_tab = "camera"
            st.rerun()

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == "upload" else "tertiary"
        if st.button("Upload Photos", type=type_upload, icon=":material/upload:", width="stretch"):
            st.session_state.photo_tab = "upload"
            st.rerun()

    if st.session_state.photo_tab == "camera":
        cam_photo = st.camera_input("Take Snapshot", key="dialog_cam")
        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast("Photo captured!")
            st.rerun()

    if st.session_state.photo_tab == "upload":
        uploaded_files = st.file_uploader(
            "Choose classroom image files",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            key="dialog_upload",
        )

        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.toast(f"{len(uploaded_files)} photo(s) uploaded!")
            st.rerun()

    st.divider()
    staged_count = len(st.session_state.get("attendance_images", []))
    if st.button(f"Done ({staged_count} staged)", type="primary", width="stretch"):
        st.rerun()
