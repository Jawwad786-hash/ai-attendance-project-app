from datetime import datetime
import uuid

import bcrypt
from postgrest.exceptions import APIError

from src.database.config import supabase


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Check for unique username, returns false when username is already taken
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0


def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher["password"]):
            return teacher
    return None


def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data


def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {"name": new_name, "face_embedding": face_embedding, "voice_embedding": voice_embedding}
    response = supabase.table("students").insert(data).execute()
    return response.data


def update_student_voice_embedding(student_id, voice_embedding):
    response = (
        supabase.table("students")
        .update({"voice_embedding": voice_embedding})
        .eq("student_id", student_id)
        .execute()
    )
    return response.data


def create_subject(subject_code, name, section, teacher_id):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id,
    }
    response = supabase.table("subjects").insert(data).execute()
    return response.data


def get_teacher_subjects(teacher_id):
    response = (
        supabase.table("subjects")
        .select("*, subject_students(count), attendance_logs(timestamp, session_id)")
        .eq("teacher_id", teacher_id)
        .execute()
    )
    subjects = response.data or []

    for sub in subjects:
        sub["total_students"] = (
            sub.get("subject_students", [{}])[0].get("count", 0)
            if sub.get("subject_students")
            else 0
        )
        attendance = sub.get("attendance_logs") or []
        unique_sessions = len(
            {
                log["session_id"]
                if log.get("session_id")
                else f"legacy_{sub['subject_id']}_{log.get('timestamp')}"
                for log in attendance
            }
        )
        sub["total_classes"] = unique_sessions

        sub.pop("subject_students", None)
        sub.pop("subject_student", None)
        sub.pop("attendance_logs", None)

    return subjects


def verify_teacher_owns_subject(teacher_id, subject_id):
    response = (
        supabase.table("subjects")
        .select("subject_id, subject_code, name, section, teacher_id")
        .eq("subject_id", int(subject_id))
        .eq("teacher_id", int(teacher_id))
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def get_enrolled_students_for_subject(subject_id):
    response = (
        supabase.table("subject_students")
        .select("*, students(*)")
        .eq("subject_id", int(subject_id))
        .execute()
    )
    return response.data or []


def _is_fk_violation(exc):
    code = getattr(exc, "code", None)
    if code == "23503":
        return True
    msg = str(exc).lower()
    return "23503" in msg or "foreign key" in msg


def get_subject_linked_counts(teacher_id, subject_id):
    subject = verify_teacher_owns_subject(teacher_id, subject_id)
    if not subject:
        raise PermissionError("You are not authorized to access or delete this subject.")

    enrolled_rows = (
        supabase.table("subject_students")
        .select("student_id")
        .eq("subject_id", int(subject_id))
        .execute()
        .data
        or []
    )
    attendance_rows = (
        supabase.table("attendance_logs")
        .select("attendance_id")
        .eq("subject_id", int(subject_id))
        .execute()
        .data
        or []
    )

    enrolled_count = len(enrolled_rows)
    attendance_count = len(attendance_rows)
    return {
        "subject": subject,
        "enrolled_count": enrolled_count,
        "attendance_count": attendance_count,
        "can_delete": enrolled_count == 0 and attendance_count == 0,
    }


def delete_subject(teacher_id, subject_id):
    link_info = get_subject_linked_counts(teacher_id, subject_id)
    subject = link_info["subject"]
    enrolled_count = link_info["enrolled_count"]
    attendance_count = link_info["attendance_count"]

    if not link_info["can_delete"]:
        return {
            "deleted": False,
            "blocked_by_links": True,
            "enrolled_count": enrolled_count,
            "attendance_count": attendance_count,
            "message": (
                f"Cannot delete '{subject['name']}' because it has "
                f"{enrolled_count} enrolled student(s) and {attendance_count} attendance log(s)."
            ),
        }

    try:
        response = (
            supabase.table("subjects")
            .delete()
            .eq("subject_id", int(subject_id))
            .eq("teacher_id", int(teacher_id))
            .execute()
        )
    except APIError as exc:
        if _is_fk_violation(exc):
            return {
                "deleted": False,
                "blocked_by_links": True,
                "enrolled_count": enrolled_count,
                "attendance_count": attendance_count,
                "message": (
                    f"Cannot delete '{subject['name']}' because linked records reference this subject."
                ),
            }
        raise

    deleted_rows = response.data or []
    if not deleted_rows:
        raise RuntimeError("Subject could not be deleted or was already removed.")

    return {
        "deleted": True,
        "blocked_by_links": False,
        "enrolled_count": 0,
        "attendance_count": 0,
        "message": f"Deleted '{subject['name']}' ({subject['subject_code']}).",
    }


def enroll_student_to_subject(student_id, subject_id):
    data = {"student_id": student_id, "subject_id": subject_id}
    response = supabase.table("subject_students").insert(data).execute()
    return response.data


def unenroll_student_to_subject(student_id, subject_id):
    response = (
        supabase.table("subject_students")
        .delete()
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
        .execute()
    )
    return response.data


def get_student_subjects(student_id):
    response = (
        supabase.table("subject_students")
        .select("*, subjects(*)")
        .eq("student_id", student_id)
        .execute()
    )
    return response.data


def get_student_attendance(student_id):
    response = (
        supabase.table("attendance_logs")
        .select("*, subjects(*)")
        .eq("student_id", student_id)
        .execute()
    )
    return response.data


def generate_session_id(subject_id, session_timestamp=None):
    if session_timestamp:
        ts_clean = str(session_timestamp).replace(":", "").replace("-", "").split(".")[0]
    else:
        ts_clean = datetime.now().strftime("%Y%m%dT%H%M%S")
    return f"sess_{int(subject_id)}_{ts_clean}_{uuid.uuid4().hex[:8]}"


def _is_unique_violation(exc):
    code = getattr(exc, "code", None)
    if code == "23505":
        return True
    msg = str(exc).lower()
    return "23505" in msg or "duplicate key" in msg or "uq_attendance_student_subject_session" in msg


def _upsert_session_log_row(entry):
    student_id = int(entry["student_id"])
    subject_id = int(entry["subject_id"])
    session_id = entry["session_id"]
    is_present = bool(entry["is_present"])
    payload = {
        "student_id": student_id,
        "subject_id": subject_id,
        "timestamp": entry["timestamp"],
        "session_id": session_id,
        "is_present": is_present,
    }

    try:
        res = supabase.table("attendance_logs").insert(payload).execute()
        return res.data[0] if res.data else payload
    except APIError as exc:
        if not _is_unique_violation(exc):
            raise
        existing = (
            supabase.table("attendance_logs")
            .select("*")
            .eq("student_id", student_id)
            .eq("subject_id", subject_id)
            .eq("session_id", session_id)
            .execute()
        )
        rows = existing.data or []
        if not rows:
            raise
        attendance_id = rows[0]["attendance_id"]
        updated = (
            supabase.table("attendance_logs")
            .update({"is_present": is_present})
            .eq("attendance_id", attendance_id)
            .execute()
        )
        return updated.data[0] if updated.data else {**rows[0], "is_present": is_present}


def create_attendance(logs):
    if not logs:
        return []

    first_subject_id = logs[0]["subject_id"]
    first_ts = logs[0].get("timestamp") or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    fallback_session_id = logs[0].get("session_id") or generate_session_id(
        first_subject_id, first_ts
    )

    normalized_logs = []
    seen_keys = set()
    for log in logs:
        sid = log.get("session_id") or fallback_session_id
        key = (int(log["student_id"]), int(log["subject_id"]), sid)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        normalized_logs.append(
            {
                "student_id": int(log["student_id"]),
                "subject_id": int(log["subject_id"]),
                "timestamp": log.get("timestamp") or first_ts,
                "session_id": sid,
                "is_present": bool(log.get("is_present", False)),
            }
        )

    try:
        response = supabase.table("attendance_logs").insert(normalized_logs).execute()
        return response.data or []
    except APIError as exc:
        if not _is_unique_violation(exc):
            raise
        return [_upsert_session_log_row(entry) for entry in normalized_logs]


def get_attendance_for_teacher(teacher_id):
    response = (
        supabase.table("attendance_logs")
        .select("*, subjects!inner(*)")
        .eq("subjects.teacher_id", teacher_id)
        .execute()
    )
    return response.data or []


def get_session_attendance_for_teacher(
    teacher_id,
    subject_id,
    session_id=None,
    legacy_timestamp=None,
):
    subject = verify_teacher_owns_subject(teacher_id, subject_id)
    if not subject:
        raise PermissionError("You are not authorized to access this subject.")

    query = (
        supabase.table("attendance_logs")
        .select("attendance_id, student_id, subject_id, timestamp, is_present, session_id")
        .eq("subject_id", int(subject_id))
    )
    if session_id:
        query = query.eq("session_id", session_id)
    else:
        query = query.is_("session_id", "null").eq("timestamp", legacy_timestamp)

    session_logs = query.order("attendance_id").execute().data or []

    enrolled_nodes = get_enrolled_students_for_subject(subject_id)
    student_names = {}
    enrolled_ids = set()
    for node in enrolled_nodes:
        stu = node.get("students")
        if stu:
            sid = int(stu["student_id"])
            enrolled_ids.add(sid)
            student_names[sid] = stu.get("name", f"Student #{sid}")

    # Fetch names for any logged student who may have later unenrolled.
    missing_name_ids = {
        int(log["student_id"])
        for log in session_logs
        if int(log["student_id"]) not in student_names
    }
    if missing_name_ids:
        all_students = get_all_students() or []
        for stu in all_students:
            sid = int(stu["student_id"])
            if sid in missing_name_ids:
                student_names[sid] = stu.get("name", f"Student #{sid}")

    logs_by_student = {}
    for log in session_logs:
        logs_by_student.setdefault(int(log["student_id"]), []).append(log)

    rows = []
    ambiguous_student_ids = []

    all_student_ids = sorted(enrolled_ids | set(logs_by_student.keys()))
    for sid in all_student_ids:
        stu_logs = logs_by_student.get(sid, [])
        name = student_names.get(sid, f"Student #{sid}")
        is_enrolled = sid in enrolled_ids

        if len(stu_logs) > 1:
            ambiguous_student_ids.append(sid)
            for idx, log in enumerate(stu_logs, start=1):
                rows.append(
                    {
                        "row_key": f"aid_{log['attendance_id']}",
                        "attendance_id": int(log["attendance_id"]),
                        "student_id": sid,
                        "name": f"{name} (Record #{idx} · ID {log['attendance_id']})",
                        "is_present": bool(log.get("is_present", False)),
                        "was_logged": True,
                        "is_enrolled": is_enrolled,
                        "is_ambiguous": True,
                        "timestamp": log.get("timestamp"),
                    }
                )
        elif len(stu_logs) == 1:
            log = stu_logs[0]
            rows.append(
                {
                    "row_key": f"aid_{log['attendance_id']}",
                    "attendance_id": int(log["attendance_id"]),
                    "student_id": sid,
                    "name": name,
                    "is_present": bool(log.get("is_present", False)),
                    "was_logged": True,
                    "is_enrolled": is_enrolled,
                    "is_ambiguous": False,
                    "timestamp": log.get("timestamp"),
                }
            )
        else:
            rows.append(
                {
                    "row_key": f"stu_{sid}",
                    "attendance_id": None,
                    "student_id": sid,
                    "name": name,
                    "is_present": False,
                    "was_logged": False,
                    "is_enrolled": is_enrolled,
                    "is_ambiguous": False,
                    "timestamp": legacy_timestamp,
                }
            )

    return {
        "subject": subject,
        "session_id": session_id,
        "legacy_timestamp": legacy_timestamp,
        "rows": rows,
        "ambiguous_student_ids": ambiguous_student_ids,
    }


def save_manual_attendance_corrections(
    teacher_id,
    subject_id,
    corrections,
    session_id=None,
    session_timestamp=None,
):
    subject = verify_teacher_owns_subject(teacher_id, subject_id)
    if not subject:
        raise PermissionError("You are not authorized to modify this subject's attendance.")

    updated_count = 0
    inserted_count = 0

    for item in corrections:
        attendance_id = item.get("attendance_id")
        student_id = int(item["student_id"])
        new_status = bool(item["new_status"])

        if attendance_id is not None:
            # Update existing record strictly by attendance_id (required for legacy and existing rows).
            res = (
                supabase.table("attendance_logs")
                .update({"is_present": new_status})
                .eq("attendance_id", int(attendance_id))
                .eq("subject_id", int(subject_id))
                .execute()
            )
            if not res.data:
                raise RuntimeError(
                    f"Attendance record {attendance_id} was not found for this subject."
                )
            updated_count += 1
        elif session_id:
            # New session missing a row for this enrolled student: insert or handle 23505 conflict safely.
            entry = {
                "student_id": student_id,
                "subject_id": int(subject_id),
                "session_id": session_id,
                "timestamp": session_timestamp or datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "is_present": new_status,
            }
            try:
                supabase.table("attendance_logs").insert(entry).execute()
                inserted_count += 1
            except APIError as exc:
                if not _is_unique_violation(exc):
                    raise
                existing = (
                    supabase.table("attendance_logs")
                    .select("attendance_id")
                    .eq("student_id", student_id)
                    .eq("subject_id", int(subject_id))
                    .eq("session_id", session_id)
                    .execute()
                )
                rows = existing.data or []
                if not rows:
                    raise
                (
                    supabase.table("attendance_logs")
                    .update({"is_present": new_status})
                    .eq("attendance_id", int(rows[0]["attendance_id"]))
                    .execute()
                )
                updated_count += 1
        else:
            # Legacy session (session_id is NULL) where enrolled student was not logged yet.
            if not session_timestamp:
                raise ValueError("Legacy session timestamp is required.")
            existing = (
                supabase.table("attendance_logs")
                .select("attendance_id")
                .eq("student_id", student_id)
                .eq("subject_id", int(subject_id))
                .is_("session_id", "null")
                .eq("timestamp", session_timestamp)
                .execute()
            )
            rows = existing.data or []
            if len(rows) > 1:
                raise RuntimeError(
                    f"Ambiguous legacy records exist for student {student_id} at {session_timestamp}."
                )
            if len(rows) == 1:
                (
                    supabase.table("attendance_logs")
                    .update({"is_present": new_status})
                    .eq("attendance_id", int(rows[0]["attendance_id"]))
                    .execute()
                )
                updated_count += 1
            else:
                (
                    supabase.table("attendance_logs")
                    .insert(
                        {
                            "student_id": student_id,
                            "subject_id": int(subject_id),
                            "session_id": None,
                            "timestamp": session_timestamp,
                            "is_present": new_status,
                        }
                    )
                    .execute()
                )
                inserted_count += 1

    return {"updated": updated_count, "inserted": inserted_count}
