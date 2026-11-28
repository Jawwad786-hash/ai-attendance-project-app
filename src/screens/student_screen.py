import time
import numpy as np
import streamlit as st
from PIL import Image

from src.components.dialog_enroll import enroll_dialog
from src.components.header import header_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    create_student,
    get_all_students,
    get_student_attendance,
    get_student_subjects,
    unenroll_student_to_subject,
    update_student_voice_embedding,
)
from src.pipelines.face_pipeline import (
    get_face_embeddings,
    predict_attendance,
    train_classifier,
)
from src.pipelines.voice_pipeline import get_voice_embedding
from src.ui.base_layout import style_background_dashboard, style_base_layout


def _render_student_topbar(right_label=None, is_logged_in=False):
    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if is_logged_in and right_label:
            b1, b2 = st.columns([1.5, 1], vertical_alignment="center")
            with b1:
                st.markdown(
                    f'<div style="text-align:right;"><span class="snap-user-pill">Student · {right_label}</span></div>',
                    unsafe_allow_html=True,
                )
            with b2:
                if st.button(
                    "Logout",
                    type="secondary",
                    key="loginbackbtn",
                    icon=":material/logout:",
                    shortcut="control+backspace",
                    width="stretch",
                ):
                    st.session_state["is_logged_in"] = False
                    del st.session_state.student_data
                    st.rerun()
        else:
            _, back_col = st.columns([1, 1.3])
            with back_col:
                if st.button(
                    "Back to Home",
                    type="secondary",
                    key="loginbackbtn",
                    icon=":material/arrow_back:",
                    shortcut="control+backspace",
                    width="stretch",
                ):
                    st.session_state["login_type"] = None
                    st.rerun()


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data["student_id"]

    _render_student_topbar(right_label=student_data["name"], is_logged_in=True)
    st.divider()

    with st.container(key="snap_card_voice_enroll", border=True):
        vc1, vc2 = st.columns([3, 1.3], vertical_alignment="center")
        with vc1:
            st.subheader("Voice Profile Enrollment")
            if student_data.get("voice_embedding"):
                st.success("Voice profile already enrolled.")
            else:
                st.info("No voice profile enrolled yet. Record a short phrase for voice attendance.")
        with vc2:
            btn_label = (
                "Re-record Voice Profile"
                if student_data.get("voice_embedding")
                else "Enroll Voice Profile"
            )
            if st.button(btn_label, type="secondary", icon=":material/mic:", width="stretch"):
                st.session_state["record_voice_profile"] = True

        if st.session_state.get("record_voice_profile", False):
            voice_audio = st.audio_input(
                "Record yourself saying: I am present, My name is " + student_data["name"]
            )

            if st.button("Save Voice Profile", type="primary", icon=":material/save:"):
                if voice_audio is None:
                    st.warning("Please record your voice first.")
                else:
                    with st.spinner("Processing your voice..."):
                        embedding = get_voice_embedding(voice_audio.read())

                        if embedding is not None:
                            update_student_voice_embedding(student_id, embedding)
                            st.session_state.student_data["voice_embedding"] = embedding
                            st.session_state["record_voice_profile"] = False
                            st.success("Voice profile saved successfully!")
                            st.rerun()

    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1.3], vertical_alignment="center")
    with c1:
        st.header("Your Enrolled Subjects")
        st.markdown(
            '<p class="snap-subtitle">Track attendance across your active classes or join a new subject with a code.</p>',
            unsafe_allow_html=True,
        )
    with c2:
        if st.button(
            "Enroll in Subject",
            type="primary",
            icon=":material/add_circle:",
            width="stretch",
        ):
            enroll_dialog()

    with st.spinner("Loading your enrolled subjects..."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}
    total_sessions = 0
    total_attended = 0

    for log in logs:
        sid = log["subject_id"]
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]["total"] += 1
        total_sessions += 1
        if log.get("is_present"):
            stats_map[sid]["attended"] += 1
            total_attended += 1

    attendance_pct = (
        f"{round((total_attended / total_sessions) * 100)}%"
        if total_sessions > 0
        else "—"
    )

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Enrolled Subjects</div><div class="snap-stat-value">{len(subjects)}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Classes Attended</div><div class="snap-stat-value">{total_attended} / {total_sessions}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Overall Attendance</div><div class="snap-stat-value">{attendance_pct}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.1rem;'></div>", unsafe_allow_html=True)

    if not subjects:
        with st.container(key="snap_card_student_empty", border=True):
            st.info(
                "You aren't enrolled in any subjects yet. Click **Enroll in Subject** above to join your first class."
            )
    else:
        cols = st.columns(2, gap="medium")
        for i, sub_node in enumerate(subjects):
            sub = sub_node["subjects"]
            sid = sub["subject_id"]
            sub_name = sub["name"]
            stats = stats_map.get(sid, {"total": 0, "attended": 0})

            def unenroll_button(student_id=student_id, sid=sid, sub_name=sub_name):
                if st.button(
                    "Unenroll from this course",
                    type="tertiary",
                    key=f"unenroll_{sid}",
                    width="stretch",
                    icon=":material/delete_forever:",
                ):
                    unenroll_student_to_subject(student_id, sid)
                    st.toast(f"Unenrolled from {sub_name} successfully!")
                    st.rerun()

            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=[
                        ("📅", "Total", stats["total"]),
                        ("✅", "Attended", stats["attended"]),
                    ],
                    footer_callback=unenroll_button,
                )


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    _render_student_topbar(is_logged_in=False)
    st.divider()

    show_registration = False
    _, center_col, _ = st.columns([0.55, 2.9, 0.55])

    with center_col:
        with st.container(key="snap_card_face_login", border=True):
            st.markdown(
                """
                <div style="text-align:center; margin-bottom:0.85rem;">
                    <span class="snap-eyebrow snap-eyebrow-light">Biometric Sign-In</span>
                    <h1 style="margin:0;">Login using FaceID</h1>
                    <p class="snap-subtitle">Center your face in good lighting to sign in, or create a new profile if you aren't registered yet.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            photo_source = st.camera_input("Position your face in the center")

        if photo_source:
            img = np.array(Image.open(photo_source))

            with st.spinner("AI is scanning..."):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning("Face not found! Please make sure your face is clearly visible.")
                elif num_faces > 1:
                    st.warning("Multiple faces found. Please capture only your own face.")
                else:
                    if detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next(
                            (s for s in all_students if s["student_id"] == student_id),
                            None,
                        )

                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.student_data = student
                            st.toast(f"Welcome Back {student['name']}")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.info("Face not recognized! Complete your profile registration below.")
                        show_registration = True

        if show_registration:
            st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)
            with st.container(key="snap_card_student_register", border=True):
                st.markdown(
                    """
                    <div style="margin-bottom:0.75rem;">
                        <span class="snap-eyebrow snap-eyebrow-light">New Student</span>
                        <h2 style="margin:0;">Register New Profile</h2>
                        <p class="snap-subtitle">Your facial features will be saved securely from the snapshot above.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                new_name = st.text_input("Full Name", placeholder="E.g. Hamza Rizvi")

                st.subheader("Optional: Voice Enrollment")
                st.info("Enroll your voice so teachers can mark you present during voice attendance.")

                audio_data = None
                try:
                    audio_data = st.audio_input(
                        'Record a short phrase like "I am present, my name is Akash."'
                    )
                except Exception:
                    st.error("Audio Data failed!")

                if st.button(
                    "Create Account",
                    type="primary",
                    icon=":material/person_add:",
                    width="stretch",
                ):
                    if new_name:
                        with st.spinner("Creating profile..."):
                            img = np.array(Image.open(photo_source))
                            encodings = get_face_embeddings(img)
                            if encodings:
                                face_emb = encodings[0].tolist()

                                voice_emb = None
                                if audio_data:
                                    voice_emb = get_voice_embedding(audio_data.read())

                                response_data = create_student(
                                    new_name,
                                    face_embedding=face_emb,
                                    voice_embedding=voice_emb,
                                )

                                if response_data:
                                    train_classifier()
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = "student"
                                    st.session_state.student_data = response_data[0]
                                    st.toast(f"Profile Created! Hi {new_name}!")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("Could not capture your facial features for registration.")
                    else:
                        st.warning("Please enter your name!")
