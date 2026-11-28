import time
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from postgrest.exceptions import APIError

from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.components.header import header_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    delete_subject,
    generate_session_id,
    get_attendance_for_teacher,
    get_enrolled_students_for_subject,
    get_session_attendance_for_teacher,
    get_subject_linked_counts,
    get_teacher_subjects,
    save_manual_attendance_corrections,
    teacher_login,
    verify_teacher_owns_subject,
)
from src.pipelines.face_pipeline import predict_attendance
from src.ui.base_layout import style_background_dashboard, style_base_layout


def _is_authorized_teacher():
    return (
        st.session_state.get("user_role") == "teacher"
        and st.session_state.get("is_logged_in") is True
        and "teacher_data" in st.session_state
    )


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
    if not _is_authorized_teacher():
        st.error("Teacher authorization required.")
        return

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
                if not verify_teacher_owns_subject(teacher_id, selected_subject_id):
                    st.error("You are not authorized to run attendance for this subject.")
                    return

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

                    try:
                        enrolled_students = get_enrolled_students_for_subject(
                            selected_subject_id
                        )
                    except APIError as exc:
                        st.error(
                            f"Could not load enrolled students: {getattr(exc, 'message', str(exc))}"
                        )
                        return

                    if not enrolled_students:
                        st.warning("No students enrolled in this course.")
                    else:
                        results, attendance_to_log = [], []
                        current_timestamp = datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        )
                        session_id = generate_session_id(
                            selected_subject_id, current_timestamp
                        )

                        for node in enrolled_students:
                            student = node.get("students")
                            if not student:
                                continue
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
                                    "session_id": session_id,
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


@st.dialog("Delete Subject")
def _delete_subject_dialog(teacher_id, sub):
    if not _is_authorized_teacher():
        st.error("Teacher authorization required.")
        return

    subject_id = int(sub["subject_id"])
    st.markdown(f"**{sub['name']}** (`{sub['subject_code']}` · Section {sub['section']})")

    try:
        link_info = get_subject_linked_counts(teacher_id, subject_id)
    except PermissionError as exc:
        st.error(str(exc))
        return
    except APIError as exc:
        st.error(f"Database error checking linked records: {getattr(exc, 'message', str(exc))}")
        return
    except Exception as exc:
        st.error(f"Could not inspect subject dependencies: {exc}")
        return

    enrolled_count = link_info["enrolled_count"]
    attendance_count = link_info["attendance_count"]

    if not link_info["can_delete"]:
        st.warning(
            f"Deletion blocked: this subject still has **{enrolled_count} enrolled student(s)** "
            f"and **{attendance_count} attendance log(s)**."
        )
        st.info(
            "To prevent silently deleting or orphaning student enrollments and attendance history, "
            "subjects with linked records cannot be deleted directly. "
            "Safe handling options: keep the subject intact for historical records, or have students unenroll "
            "and use an explicitly approved archive/cleanup migration before removing historical attendance."
        )
        if st.button("Close", type="secondary", width="stretch"):
            st.rerun()
        return

    st.caption("No students or attendance logs are linked to this subject.")
    confirm_delete = st.checkbox(
        "I confirm I want to permanently delete this subject.",
        key=f"confirm_delete_sub_{subject_id}",
    )

    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("Cancel", type="secondary", width="stretch"):
            st.rerun()
    with c2:
        if st.button(
            "Confirm Delete",
            type="primary",
            icon=":material/delete:",
            disabled=not confirm_delete,
            width="stretch",
        ):
            try:
                res = delete_subject(teacher_id, subject_id)
                if res["deleted"]:
                    st.toast(res["message"])
                    st.rerun()
                else:
                    st.warning(res["message"])
            except PermissionError as exc:
                st.error(str(exc))
            except APIError as exc:
                st.error(
                    f"Database error deleting subject: {getattr(exc, 'message', str(exc))}"
                )
            except Exception as exc:
                st.error(f"Could not delete subject: {exc}")


def teacher_tab_manage_subjects():
    if not _is_authorized_teacher():
        st.error("Teacher authorization required.")
        return

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

            def card_actions(
                sub_row=sub,
                sub_id=sub["subject_id"],
                sub_name=sub["name"],
                sub_code=sub["subject_code"],
            ):
                b1, b2 = st.columns([2, 1], gap="small")
                with b1:
                    if st.button(
                        f"Share Code: {sub_code}",
                        key=f"share_{sub_code}_{sub_id}",
                        type="tertiary",
                        icon=":material/share:",
                        width="stretch",
                    ):
                        share_subject_dialog(sub_name, sub_code)
                with b2:
                    if st.button(
                        "Delete",
                        key=f"delete_sub_{sub_id}",
                        type="secondary",
                        icon=":material/delete:",
                        width="stretch",
                    ):
                        _delete_subject_dialog(teacher_id, sub_row)

            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=stats,
                    footer_callback=card_actions,
                )
    else:
        with st.container(key="snap_card_teacher_empty", border=True):
            st.info("No subjects found yet. Create one above to get started.")


def _format_session_time(ts_str):
    if not ts_str:
        return "N/A"
    try:
        return datetime.fromisoformat(str(ts_str)).strftime("%Y-%m-%d %I:%M %p")
    except ValueError:
        return str(ts_str)


def _render_manual_correction_panel(teacher_id, session_options):
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    with st.container(key="snap_card_manual_correction", border=True):
        st.subheader("Manual Attendance Correction")
        st.markdown(
            '<p class="snap-subtitle" style="margin-bottom:0.9rem;">Select a recorded session to review or correct student attendance. Confirmation is required before saving.</p>',
            unsafe_allow_html=True,
        )

        selected_label = st.selectbox(
            "Select Session to Correct",
            options=list(session_options.keys()),
            key="manual_corr_session_select",
        )
        selected_meta = session_options[selected_label]
        session_key = selected_meta["session_key"]

        try:
            session_data = get_session_attendance_for_teacher(
                teacher_id=teacher_id,
                subject_id=selected_meta["subject_id"],
                session_id=selected_meta["session_id"],
                legacy_timestamp=selected_meta["raw_timestamp"]
                if not selected_meta["session_id"]
                else None,
            )
        except PermissionError as exc:
            st.error(str(exc))
            return
        except APIError as exc:
            st.error(f"Database error loading session: {getattr(exc, 'message', str(exc))}")
            return
        except Exception as exc:
            st.error(f"Could not load session details: {exc}")
            return

        rows = session_data["rows"]
        ambiguous_ids = session_data["ambiguous_student_ids"]

        if ambiguous_ids:
            st.warning(
                "Ambiguous legacy records were detected for this timestamp (multiple rows exist for the same student). "
                "Each record is listed separately by `attendance_id` below and will not be merged."
            )

        if not rows:
            st.info("No enrolled students or attendance rows found for this session.")
            return

        st.markdown("---")
        pending_changes = []

        for row in rows:
            rkey = row["row_key"]
            widget_key = f"corr_{session_key}_{rkey}"
            original_present = bool(row["is_present"])

            c_name, c_orig, c_new = st.columns([2.4, 1.2, 1.4], vertical_alignment="center")
            with c_name:
                extra = ""
                if not row["is_enrolled"]:
                    extra = " · Unenrolled"
                elif not row["was_logged"]:
                    extra = " · Not originally logged"
                st.markdown(
                    f"**{row['name']}**  \n"
                    f"<span style='color:#64748B; font-size:0.84rem;'>ID {row['student_id']}{extra}</span>",
                    unsafe_allow_html=True,
                )
            with c_orig:
                badge = "✅ Present" if original_present else "❌ Absent"
                st.caption(f"Current: {badge}")
            with c_new:
                new_present = st.checkbox(
                    "Mark Present",
                    value=original_present,
                    key=widget_key,
                )

            if bool(new_present) != original_present:
                pending_changes.append(
                    {
                        "attendance_id": row["attendance_id"],
                        "student_id": row["student_id"],
                        "name": row["name"],
                        "previous_status": original_present,
                        "new_status": bool(new_present),
                    }
                )

        st.markdown("---")

        if pending_changes:
            summary_lines = [
                f"- **{chg['name']}**: {'Present' if chg['previous_status'] else 'Absent'} → "
                f"**{'Present' if chg['new_status'] else 'Absent'}**"
                for chg in pending_changes
            ]
            st.info("Pending changes to save:\n" + "\n".join(summary_lines))
        else:
            st.caption("Toggle one or more students above to make a correction.")

        confirm_key = f"confirm_corr_{session_key}"
        if st.session_state.pop("reset_corr_confirm_for", None) == confirm_key:
            st.session_state[confirm_key] = False

        confirmed = st.checkbox(
            "I confirm I want to save these attendance status corrections.",
            key=confirm_key,
            disabled=not pending_changes,
        )

        if st.button(
            "Save Corrections",
            type="primary",
            icon=":material/check_circle:",
            disabled=not (pending_changes and confirmed),
            width="stretch",
        ):
            if not _is_authorized_teacher():
                st.error("Teacher authorization required.")
                return
            try:
                result = save_manual_attendance_corrections(
                    teacher_id=teacher_id,
                    subject_id=selected_meta["subject_id"],
                    corrections=pending_changes,
                    session_id=selected_meta["session_id"],
                    session_timestamp=selected_meta["raw_timestamp"],
                )
                st.session_state["reset_corr_confirm_for"] = confirm_key
                st.toast(
                    f"Saved corrections ({result['updated']} updated, {result['inserted']} added)."
                )
                st.success(
                    f"Corrections saved ({result['updated']} updated, {result['inserted']} added)."
                )
                st.rerun()
            except (PermissionError, ValueError, RuntimeError) as exc:
                st.error(str(exc))
            except APIError as exc:
                st.error(f"Database error saving corrections: {getattr(exc, 'message', str(exc))}")
            except Exception as exc:
                st.error(f"Unexpected error saving corrections: {exc}")


def teacher_tab_attendance_records():
    if not _is_authorized_teacher():
        st.error("Teacher authorization required.")
        return

    st.header("Attendance Records")
    st.markdown(
        '<p class="snap-subtitle" style="margin-bottom:1rem;">Overview of recorded attendance sessions and manual corrections.</p>',
        unsafe_allow_html=True,
    )

    teacher_id = st.session_state.teacher_data["teacher_id"]
    try:
        records = get_attendance_for_teacher(teacher_id)
    except APIError as exc:
        st.error(f"Could not load attendance records: {getattr(exc, 'message', str(exc))}")
        return
    except Exception as exc:
        st.error(f"Could not load attendance records: {exc}")
        return

    if not records:
        with st.container(key="snap_card_records_empty", border=True):
            st.info("No attendance records logged yet.")
        return

    grouped = {}
    for r in records:
        ts = r.get("timestamp")
        sub = r.get("subjects") or {}
        sub_id = int(r["subject_id"])
        sid = r.get("session_id")
        if sid:
            session_key = f"sid:{sid}"
        else:
            session_key = f"legacy:{sub_id}:{ts}"

        bucket = grouped.setdefault(
            session_key,
            {
                "session_key": session_key,
                "session_id": sid,
                "subject_id": sub_id,
                "raw_timestamp": ts or "",
                "sort_key": str(ts or ""),
                "time_display": _format_session_time(ts),
                "subject_name": sub.get("name", ""),
                "subject_code": sub.get("subject_code", ""),
                "present_count": 0,
                "total_count": 0,
            },
        )
        bucket["total_count"] += 1
        if r.get("is_present"):
            bucket["present_count"] += 1

    sessions = sorted(grouped.values(), key=lambda s: s["sort_key"], reverse=True)

    total_present = sum(s["present_count"] for s in sessions)
    total_possible = sum(s["total_count"] for s in sessions)
    avg_rate = (
        f"{round((total_present / total_possible) * 100)}%"
        if total_possible > 0
        else "—"
    )

    m1, m2 = st.columns(2, gap="medium")
    with m1:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Recorded Sessions</div><div class="snap-stat-value">{len(sessions)}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="snap-stat-box"><div class="snap-stat-label">Average Attendance</div><div class="snap-stat-value">{avg_rate}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

    display_rows = [
        {
            "Time": s["time_display"],
            "Subject": s["subject_name"],
            "Subject Code": s["subject_code"],
            "Session Type": "Session ID" if s["session_id"] else "Legacy",
            "Attendance Stats": f"✅ {s['present_count']} / {s['total_count']} Students",
        }
        for s in sessions
    ]
    st.dataframe(pd.DataFrame(display_rows), width="stretch", hide_index=True)

    session_options = {}
    for s in sessions:
        tag = "" if s["session_id"] else " [Legacy]"
        label = (
            f"{s['time_display']} — {s['subject_name']} ({s['subject_code']}){tag}"
        )
        # Ensure label uniqueness if two sessions share the same minute/second display.
        if label in session_options:
            short_id = s["session_id"][-6:] if s["session_id"] else s["raw_timestamp"][-6:]
            label = f"{label} [{short_id}]"
        session_options[label] = s

    _render_manual_correction_panel(teacher_id, session_options)


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
