import time
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.components.header import header_dashboard
from src.components.subject_card import subject_card
from src.database.config import supabase
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    get_attendance_for_teacher,
    get_teacher_subjects,
    teacher_login,
)
from src.pipelines.face_pipeline import predict_attendance
from src.ui.base_layout import style_background_dashboard, style_base_layout


def _render_teacher_topbar(right_label=None, is_logged_in=False):
    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if is_logged_in and right_label:
            b1, b2 = st.columns([1.5, 1], vertical_alignment="center")
            with b1:
                st.markdown(
                    f'<div style="text-align:right;"><span class="snap-user-pill">Teacher · {right_label}</span></div>',
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
                    del st.session_state.teacher_data
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


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif (
        "teacher_login_type" not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    _render_teacher_topbar(right_label=teacher_data["name"], is_logged_in=True)
    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    with st.container(key="snap_tabbar", border=True):
        tab1, tab2, tab3 = st.columns(3, gap="small")

        with tab1:
            type1 = (
                "primary"
                if st.session_state.current_teacher_tab == "take_attendance"
                else "tertiary"
            )
            if st.button(
                "Take Attendance",
                type=type1,
                width="stretch",
                icon=":material/ar_on_you:",
            ):
                st.session_state.current_teacher_tab = "take_attendance"
                st.rerun()

        with tab2:
            type2 = (
                "primary"
                if st.session_state.current_teacher_tab == "manage_subjects"
                else "tertiary"
            )
            if st.button(
                "Manage Subjects",
                type=type2,
                width="stretch",
                icon=":material/book_ribbon:",
            ):
                st.session_state.current_teacher_tab = "manage_subjects"
                st.rerun()

        with tab3:
            type3 = (
                "primary"
                if st.session_state.current_teacher_tab == "attendance_records"
                else "tertiary"
            )
            if st.button(
                "Attendance Records",
                type=type3,
                width="stretch",
                icon=":material/cards_stack:",
            ):
                st.session_state.current_teacher_tab = "attendance_records"
                st.rerun()

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendance")
    st.markdown(
        '<p class="snap-subtitle" style="margin-bottom:1rem;">Choose a class, then analyze classroom snapshots or voice audio.</p>',
        unsafe_allow_html=True,
    )

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        with st.container(key="snap_card_no_subjects", border=True):
            st.warning(
                "You haven't created any subjects yet! Switch to **Manage Subjects** to create one."
            )
        return

    subject_options = {
        f"{s['name']} - {s['subject_code']}": s["subject_id"] for s in subjects
    }

    with st.container(key="snap_card_take_attendance", border=True):
        col1, col2 = st.columns([3, 1.2], vertical_alignment="bottom")

        with col1:
            selected_subject_label = st.selectbox(
                "Select Subject", options=list(subject_options.keys())
            )

        with col2:
            if st.button(
                "Add Photos",
                type="primary",
                icon=":material/photo_prints:",
                width="stretch",
            ):
                add_photos_dialog()

        selected_subject_id = subject_options[selected_subject_label]

        if st.session_state.attendance_images:
            st.divider()
            st.subheader(
                f"Staged Classroom Photos ({len(st.session_state.attendance_images)})"
            )
            gallery_cols = st.columns(4, gap="small")
            for idx, img in enumerate(st.session_state.attendance_images):
                with gallery_cols[idx % 4]:
                    st.image(img, width="stretch", caption=f"Photo {idx + 1}")
        else:
            st.info(
                "Click **Add Photos** to capture or upload classroom images, or launch **Use Voice Attendance** directly."
            )

        st.divider()

        has_photos = bool(st.session_state.attendance_images)
        c1, c2, c3 = st.columns(3, gap="small")

        with c1:
            if st.button(
                "Clear all photos",
                width="stretch",
                type="tertiary",
                icon=":material/delete:",
                disabled=not has_photos,
            ):
                st.session_state.attendance_images = []
                st.rerun()

        with c2:
            if st.button(
                "Run Face Analysis",
                width="stretch",
                type="secondary",
                icon=":material/analytics:",
                disabled=not has_photos,
            ):
                with st.spinner("Deep scanning classroom photos..."):
                    all_detected_ids = {}

                    for idx, img in enumerate(st.session_state.attendance_images):
                        img_np = np.array(img.convert("RGB"))
                        detected, _, _ = predict_attendance(img_np)

                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)
                                all_detected_ids.setdefault(student_id, []).append(
                                    f"Photo {idx + 1}"
                                )

                    enrolled_res = (
                        supabase.table("subject_students")
                        .select("*, students(*)")
                        .eq("subject_id", selected_subject_id)
                        .execute()
                    )
                    enrolled_students = enrolled_res.data

                    if not enrolled_students:
                        st.warning("No students enrolled in this course.")
                    else:
                        results, attendance_to_log = [], []
                        current_timestamp = datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        )

                        for node in enrolled_students:
                            student = node["students"]
                            sources = all_detected_ids.get(
                                int(student["student_id"]), []
                            )
                            is_present = len(sources) > 0

                            results.append(
                                {
                                    "Name": student["name"],
                                    "ID": student["student_id"],
                                    "Source": ", ".join(sources) if is_present else "-",
                                    "Status": "✅ Present"
                                    if is_present
                                    else "❌ Absent",
                                }
                            )

                            attendance_to_log.append(
                                {
                                    "student_id": student["student_id"],
                                    "subject_id": selected_subject_id,
                                    "timestamp": current_timestamp,
                                    "is_present": bool(is_present),
                                }
                            )

                        attendance_result_dialog(
                            pd.DataFrame(results), attendance_to_log
                        )

        with c3:
            if st.button(
                "Use Voice Attendance",
                type="primary",
                width="stretch",
                icon=":material/mic:",
            ):
                voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    col1, col2 = st.columns([3, 1.3], vertical_alignment="center")
    with col1:
        st.header("Manage Subjects")
        st.markdown(
            '<p class="snap-subtitle">Create classes and share enrollment links or QR codes with your students.</p>',
            unsafe_allow_html=True,
        )

    with col2:
        if st.button(
            "Create New Subject",
            type="primary",
            icon=":material/add_circle:",
            width="stretch",
        ):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)

    total_subjects = len(subjects) if subjects else 0
    total_enrolled = sum(s.get("total_students", 0) for s in (subjects or []))
    total_classes = sum(s.get("total_classes", 0) for s in (subjects or []))

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Active Subjects</div><div class="snap-stat-value">{total_subjects}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Total Enrollments</div><div class="snap-stat-value">{total_enrolled}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Classes Held</div><div class="snap-stat-value">{total_classes}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if subjects:
        cols = st.columns(2, gap="medium")
        for i, sub in enumerate(subjects):
            stats = [
                ("🫂", "Students", sub["total_students"]),
                ("🕰️", "Classes", sub["total_classes"]),
            ]

            def share_btn(sub_name=sub["name"], sub_code=sub["subject_code"]):
                if st.button(
                    f"Share Code: {sub_name}",
                    key=f"share_{sub_code}",
                    type="tertiary",
                    icon=":material/share:",
                    width="stretch",
                ):
                    share_subject_dialog(sub_name, sub_code)

            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=stats,
                    footer_callback=share_btn,
                )
    else:
        with st.container(key="snap_card_teacher_empty", border=True):
            st.info("No subjects found yet. Create one above to get started.")


def teacher_tab_attendance_records():
    st.header("Attendance Records")
    st.markdown(
        '<p class="snap-subtitle" style="margin-bottom:1rem;">Overview of all recorded attendance sessions across your subjects.</p>',
        unsafe_allow_html=True,
    )

    teacher_id = st.session_state.teacher_data["teacher_id"]
    records = get_attendance_for_teacher(teacher_id)

    if not records:
        with st.container(key="snap_card_records_empty", border=True):
            st.info("No attendance records logged yet.")
        return

    data = []
    for r in records:
        ts = r.get("timestamp")
        data.append(
            {
                "ts_group": ts.split(".")[0] if ts else None,
                "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p")
                if ts
                else "N/A",
                "Subject": r["subjects"]["name"],
                "Subject Code": r["subjects"]["subject_code"],
                "is_present": bool(r.get("is_present", False)),
            }
        )

    df = pd.DataFrame(data)
    summary = (
        df.groupby(["ts_group", "Time", "Subject", "Subject Code"])
        .agg(
            Present_Count=("is_present", "sum"),
            Total_Count=("is_present", "count"),
        )
        .reset_index()
    )

    total_present = int(summary["Present_Count"].sum())
    total_possible = int(summary["Total_Count"].sum())
    avg_rate = (
        f"{round((total_present / total_possible) * 100)}%"
        if total_possible > 0
        else "—"
    )

    m1, m2 = st.columns(2, gap="medium")
    with m1:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Recorded Sessions</div><div class="snap-stat-value">{len(summary)}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Average Attendance</div><div class="snap-stat-value">{avg_rate}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

    summary["Attendance Stats"] = (
        "✅ "
        + summary["Present_Count"].astype(str)
        + " / "
        + summary["Total_Count"].astype(str)
        + " Students"
    )

    display_df = summary.sort_values(by="ts_group", ascending=False)[
        ["Time", "Subject", "Subject Code", "Attendance Stats"]
    ]

    st.dataframe(display_df, width="stretch", hide_index=True)


def login_teacher(username, password):
    if not username or not password:
        return False

    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True

    return False


def teacher_screen_login():
    _render_teacher_topbar(is_logged_in=False)
    st.divider()

    _, center_col, _ = st.columns([0.9, 2.2, 0.9])
    with center_col:
        with st.container(key="snap_card_teacher_login", border=True):
            st.markdown(
                """
                <div style="text-align:center; margin-bottom:0.85rem;">
                    <span class="snap-eyebrow snap-eyebrow-light">Instructor Access</span>
                    <h1 style="margin:0;">Teacher Login</h1>
                    <p class="snap-subtitle">Sign in with your username and password to manage classes.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            teacher_username = st.text_input("Username", placeholder="ananyaroy")
            teacher_pass = st.text_input(
                "Password", type="password", placeholder="Enter password"
            )

            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            btnc1, btnc2 = st.columns(2, gap="small")

            with btnc1:
                if st.button(
                    "Login",
                    type="primary",
                    icon=":material/passkey:",
                    shortcut="control+enter",
                    width="stretch",
                ):
                    if login_teacher(teacher_username, teacher_pass):
                        st.toast("Welcome back!", icon="👋")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username and password combination.")

            with btnc2:
                if st.button(
                    "Register Instead",
                    type="secondary",
                    icon=":material/person_add:",
                    width="stretch",
                ):
                    st.session_state.teacher_login_type = "register"
                    st.rerun()


def register_teacher(
    teacher_username, teacher_name, teacher_pass, teacher_pass_confirm
):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken."
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match."

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Successfully created! You can now log in."
    except Exception:
        return False, "Unexpected error while creating account."


def teacher_screen_register():
    _render_teacher_topbar(is_logged_in=False)
    st.divider()

    _, center_col, _ = st.columns([0.9, 2.2, 0.9])
    with center_col:
        with st.container(key="snap_card_teacher_register", border=True):
            st.markdown(
                """
                <div style="text-align:center; margin-bottom:0.85rem;">
                    <span class="snap-eyebrow snap-eyebrow-light">New Instructor</span>
                    <h1 style="margin:0;">Create Teacher Account</h1>
                    <p class="snap-subtitle">Set up your profile to create subjects and take AI attendance.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            teacher_username = st.text_input("Username", placeholder="ananyaroy")
            teacher_name = st.text_input("Full Name", placeholder="Ananya Roy")
            teacher_pass = st.text_input(
                "Password", type="password", placeholder="Create password"
            )
            teacher_pass_confirm = st.text_input(
                "Confirm Password", type="password", placeholder="Confirm password"
            )

            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            btnc1, btnc2 = st.columns(2, gap="small")

            with btnc1:
                if st.button(
                    "Register now",
                    type="primary",
                    icon=":material/passkey:",
                    shortcut="control+enter",
                    width="stretch",
                ):
                    success, message = register_teacher(
                        teacher_username,
                        teacher_name,
                        teacher_pass,
                        teacher_pass_confirm,
                    )
                    if success:
                        st.success(message)
                        time.sleep(2)
                        st.session_state.teacher_login_type = "login"
                        st.rerun()
                    else:
                        st.error(message)

            with btnc2:
                if st.button(
                    "Login Instead",
                    type="secondary",
                    icon=":material/login:",
                    width="stretch",
                ):
                    st.session_state.teacher_login_type = "login"
                    st.rerun()
