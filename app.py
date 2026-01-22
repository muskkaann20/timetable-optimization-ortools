import streamlit as st
import pandas as pd

from src.model import solve_timetable

# =====================================
# Page Config
# =====================================
st.set_page_config(
    page_title="Timetable Optimizer",
    layout="wide"
)

st.title("📅 Timetable Optimization System")
st.caption("Built using Google OR-Tools (CP-SAT) + Streamlit")
st.markdown("---")

# =====================================
# Session State Init
# =====================================
if "schedule_df" not in st.session_state:
    st.session_state.schedule_df = None
    st.session_state.metrics = None

# =====================================
# 📥 Upload Input Data
# =====================================
st.markdown("## 📥 Upload Input CSV Files")

courses_file = st.file_uploader("Upload Courses CSV", type=["csv"])
rooms_file = st.file_uploader("Upload Rooms CSV", type=["csv"])
professors_file = st.file_uploader("Upload Professors CSV", type=["csv"])
slots_file = st.file_uploader("Upload Time Slots CSV", type=["csv"])

# =====================================
# 📊 Load & Preview Data
# =====================================
if courses_file and rooms_file and professors_file and slots_file:
    try:
        courses_df = pd.read_csv(courses_file, encoding="utf-8", engine="python")
        rooms_df = pd.read_csv(rooms_file, encoding="utf-8", engine="python")
        professors_df = pd.read_csv(professors_file, encoding="utf-8", engine="python")
        slots_df = pd.read_csv(slots_file, encoding="utf-8", engine="python")
    except Exception:
        st.error("❌ Invalid CSV format. Please upload valid CSV files.")
        st.stop()

    st.success("✅ All input files loaded successfully")

    with st.expander("🔍 Preview Uploaded Data"):
        st.subheader("Courses")
        st.dataframe(courses_df)

        st.subheader("Rooms")
        st.dataframe(rooms_df)

        st.subheader("Professors")
        st.dataframe(professors_df)

        st.subheader("Time Slots")
        st.dataframe(slots_df)
else:
    st.info("⬆ Please upload all four CSV files to continue")

st.markdown("---")


# =====================================
# 🚀 Generate Timetable
# =====================================
if st.button("🚀 Generate Optimized Timetable"):
    if not (courses_file and rooms_file and professors_file and slots_file):
        st.error("❌ Please upload all CSV files first")
        st.stop()

    st.info("⚙️ Running optimization model...")

    schedule_df, metrics = solve_timetable(
        courses_df, rooms_df, professors_df, slots_df
    )

    st.session_state.schedule_df = schedule_df
    st.session_state.metrics = metrics

    st.success("✅ Timetable generated successfully!")

# =====================================
# 📅 Display Timetable (ONLY after run)
# =====================================
if st.session_state.schedule_df is not None:
    st.markdown("## 📅 Optimized Timetable")
    st.dataframe(st.session_state.schedule_df)

    csv = st.session_state.schedule_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Timetable CSV",
        csv,
        "optimized_timetable.csv",
        "text/csv"
    )

# =====================================
# 📊 Optimization Metrics
# =====================================
if st.session_state.metrics is not None:
    st.markdown("## 📊 Optimization Metrics")

    c1, c2, c3 = st.columns(3)

    c1.metric("Conflicts", st.session_state.metrics.get("conflicts", 0))
    c2.metric(
        "Professor Idle Gaps",
        st.session_state.metrics.get("professor_idle_gaps", 0)
    )
    c3.metric(
        "Room Switches",
        st.session_state.metrics.get("room_switches", 0)
    )

st.markdown("---")
st.caption("© 2026 Muskaan Manwanii | Timetable Optimization using OR-Tools")
