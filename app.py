import streamlit as st
import pandas as pd
import json
import os

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
    courses_df = pd.read_csv(courses_file)
    rooms_df = pd.read_csv(rooms_file)
    professors_df = pd.read_csv(professors_file)
    slots_df = pd.read_csv(slots_file)

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

from src.model import solve_timetable


# =====================================
# 🚀 Generate Timetable
# =====================================
if st.button("🚀 Generate Optimized Timetable"):
    if not (courses_file and rooms_file and professors_file and slots_file):
        st.error("❌ Please upload all CSV files first")
    else:
        st.info("⚙️ Running optimization model...")

        schedule_df, metrics = solve_timetable(
            courses_df, rooms_df, professors_df, slots_df
        )

        st.success("✅ Timetable generated!")

        st.markdown("## 📅 Optimized Timetable")
        st.dataframe(schedule_df)

        st.markdown("## 📊 Optimization Metrics")
        c1, c2, c3 = st.columns(3)

        c1.metric("Conflicts", metrics.get("conflicts", 0))
        c2.metric("Professor Idle Gaps", metrics.get("professor_idle_gaps", 0))
        c3.metric("Room Switches", metrics.get("room_switches", 0))


# =====================================
# 📅 Display Timetable
# =====================================
if os.path.exists("results/schedule.csv"):
    st.markdown("## 📅 Optimized Timetable")

    schedule_df = pd.read_csv("results/schedule.csv")
    st.dataframe(schedule_df)

    csv = schedule_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Timetable CSV",
        csv,
        "optimized_timetable.csv",
        "text/csv"
    )

st.markdown("---")

# =====================================
# 📊 Optimization Metrics
# =====================================
if os.path.exists("results/metrics.json"):
    with open("results/metrics.json") as f:
        metrics_data = json.load(f)

    metrics = metrics_data.get("metrics", {})

    st.markdown("## 📈 Optimization Metrics")

    c1, c2, c3 = st.columns(3)

    c1.metric("Conflicts", metrics.get("conflicts", 0))
    c2.metric("Professor Idle Gaps", metrics.get("professor_idle_gaps", 0))
    c3.metric("Room Switches", metrics.get("room_switches", 0))

else:
    st.info("ℹ️ Metrics will appear after optimization")

st.markdown("---")
st.caption("© 2026 Muskaan Manwani | Timetable Optimization using OR-Tools")
