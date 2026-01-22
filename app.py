import streamlit as st
import pandas as pd
import json
import subprocess
import os

st.set_page_config(page_title="Timetable Optimizer", layout="wide")

st.title("📅 Timetable Optimization System")
st.caption("Built using OR-Tools + Streamlit")

st.markdown("---")

# =====================
# Sidebar
# =====================
st.sidebar.header("⚙️ Controls")

run_model = st.sidebar.button("🚀 Generate Optimized Timetable")

st.sidebar.markdown("---")
st.sidebar.info(
    "This app optimizes university timetables while minimizing:\n"
    "- Professor idle gaps\n"
    "- Room switches\n"
    "- Late time slots"
)

# =====================
# Data Preview
# =====================
st.subheader("📂 Input Data Preview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Courses")
    courses_df = pd.read_csv("data/courses.csv")
    st.dataframe(courses_df)

with col2:
    st.markdown("### Rooms")
    rooms_df = pd.read_csv("data/rooms.csv")
    st.dataframe(rooms_df)

st.markdown("### Time Slots")
slots_df = pd.read_csv("data/time_slots.csv")
st.dataframe(slots_df)

st.markdown("---")

# =====================
# Run Optimization
# =====================
if run_model:
    st.info("Running optimization model... ⏳")

    try:
        subprocess.run(
            ["python", "-m", "src.model"],
            check=True
        )
        st.success("Optimization completed successfully! ✅")
    except subprocess.CalledProcessError:
        st.error("Error running optimization model ❌")

# =====================
# Results Section
# =====================
st.subheader("📊 Optimization Results")

if os.path.exists("results/schedule.csv"):
    schedule_df = pd.read_csv("results/schedule.csv")
    st.markdown("### 🗓 Optimized Timetable")
    st.dataframe(schedule_df)

    st.download_button(
        "⬇️ Download Timetable CSV",
        schedule_df.to_csv(index=False),
        file_name="optimized_schedule.csv",
        mime="text/csv"
    )
else:
    st.warning("Run the model to generate timetable")

st.markdown("---")

if os.path.exists("results/metrics.json"):
    with open("results/metrics.json") as f:
        metrics = json.load(f)

    st.markdown("### 📈 Optimization Metrics")

    m1, m2, m3 = st.columns(3)

    metric_data = metrics.get("metrics", {})

    m1.metric("Conflicts", metric_data.get("conflicts", 0))
    m2.metric("Professor Idle Gaps", metric_data.get("professor_idle_gaps", 0))
    m3.metric("Room Switches", metric_data.get("room_switches", 0))



else:
    st.warning("Metrics not available yet")

st.markdown("---")
st.caption("© 2026 Muskaan Manwanii | Timetable Optimization using OR-Tools")
