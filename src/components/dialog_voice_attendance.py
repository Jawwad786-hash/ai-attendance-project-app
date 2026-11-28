from datetime import datetime
import pandas as pd
import streamlit as st

from src.components.dialog_attendance_results import show_attendance_result
from src.database.config import supabase
from src.database.db import generate_session_id
from src.pipelines.voice_pipeline import process_bulk_audio


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write(
        "Record audio of students saying I am present. "
        "Then AI will recognize their voices."
    )

    audio_data = st.audio_input("Record classroom audio")

    if st.button("Analyze Audio", width="stretch", type="primary"):
        if audio_data is None:
            st.warning("Please record classroom audio first.")
            return

        with st.spinner("Processing Audio data"):
            audio_bytes = audio_data.read()

            enrolled_res = (
                supabase.table("subject_students")
                .select("*, students(*)")
                .eq("subject_id", selected_subject_id)
                .execute()
            )
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning("No students enrolled in this course")
                return

            candidates_dict = {
                s["students"]["student_id"]: s["students"]["voice_embedding"]
                for s in enrolled_students
                if s.get("students") and s["students"].get("voice_embedding")
            }

            if not candidates_dict:
                st.error("No enrolled students have voice profiles registered.")
                return

            identified_results = process_bulk_audio(audio_bytes, candidates_dict)

            if not identified_results:
                st.warning("No matching student voices detected.")
                return

            session_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            session_id = generate_session_id(selected_subject_id, session_timestamp)
            attendance_data = []

            for student_id, score in identified_results.items():
                is_present = bool(score >= 0.65)
                attendance_data.append(
                    {
                        "student_id": int(student_id),
                        "subject_id": int(selected_subject_id),
                        "session_id": session_id,
                        "timestamp": session_timestamp,
                        "is_present": is_present,
                    }
                )

            if attendance_data:
                df = pd.DataFrame(attendance_data)
                st.session_state.voice_attendance_results = df
                st.session_state.attendance_images = []

                st.success("Voice attendance analyzed successfully!")
                show_attendance_result(df, attendance_data)
