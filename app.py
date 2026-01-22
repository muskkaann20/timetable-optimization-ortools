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

# --- NEW: Data Format Guide ---
with st.expander("ℹ️ Click to see required CSV Columns & Formats", expanded=False):
    st.markdown("""
    **Ensure your CSV files match these exact headers:**
    
    1️⃣ **courses.csv**
    * **Columns:** `course_id`, `professor_id`, `required_sessions`, `enrolled_students`
    * *Example:* `CS101, Prof_A, 3, 50`
    
    2️⃣ **rooms.csv**
    * **Columns:** `room_id`, `capacity`
    * *Example:* `Room_101, 60`
    
    3️⃣ **professors.csv**
    * **Columns:** `professor_id`, `available_slots`
    * *Note:* Separate multiple slots with a semicolon (`;`)
    * *Example:* `Prof_A, Mon_09:00;Mon_10:00`
    
    4️⃣ **slots.csv**
    * **Columns:** `slot_id`
    * *Example:* `Mon_09:00`
    """)
    
    # Optional: Download Sample Templates Button
    # You could add logic here to download sample files if needed
# ------------------------------

c1, c2 = st.columns(2)

with c1:
    courses_file = st.file_uploader("Upload Courses CSV", type=["csv"], help="Required columns: course_id, professor_id, required_sessions, enrolled_students")
    rooms_file = st.file_uploader("Upload Rooms CSV", type=["csv"], help="Required columns: room_id, capacity")

with c2:
    professors_file = st.file_uploader("Upload Professors CSV", type=["csv"], help="Required columns: professor_id, available_slots")
    slots_file = st.file_uploader("Upload Time Slots CSV", type=["csv"], help="Required columns: slot_id")

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
        # Load Data
        courses_df = pd.read_csv(courses_file)
        rooms_df = pd.read_csv(rooms_file)
        professors_df = pd.read_csv(professors_file)
        slots_df = pd.read_csv(slots_file)

        # ==========================================
        # 🧹 DATA CLEANING (Strip Invisible Spaces)
        # ==========================================
        # 1. Strip whitespace from column names
        courses_df.columns = courses_df.columns.str.strip()
        rooms_df.columns = rooms_df.columns.str.strip()
        professors_df.columns = professors_df.columns.str.strip()
        slots_df.columns = slots_df.columns.str.strip()

        # 2. Strip whitespace from text data (IDs, etc.)
        courses_df["course_id"] = courses_df["course_id"].astype(str).str.strip()
        courses_df["professor_id"] = courses_df["professor_id"].astype(str).str.strip()
        
        rooms_df["room_id"] = rooms_df["room_id"].astype(str).str.strip()
        
        professors_df["professor_id"] = professors_df["professor_id"].astype(str).str.strip()
        
        # Clean the semicolon-separated list: split, strip each item, join back
        professors_df["available_slots"] = professors_df["available_slots"].astype(str).apply(
            lambda x: ";".join([s.strip() for s in x.split(";")])
        )

        slots_df["slot_id"] = slots_df["slot_id"].astype(str).str.strip()

        # -----------------------------------------------
        # VALIDATION: Check for required columns
        # -----------------------------------------------
        required_columns = {
            "courses_df": ["course_id", "professor_id", "required_sessions", "enrolled_students"],
            "rooms_df": ["room_id", "capacity"],
            "professors_df": ["professor_id", "available_slots"],
            "slots_df": ["slot_id"]
        }

        # Check Courses
        if not set(required_columns["courses_df"]).issubset(courses_df.columns):
            st.error(f"❌ Courses CSV is missing columns. Required: {required_columns['courses_df']}")
            st.stop()
            
        # Check Rooms
        if not set(required_columns["rooms_df"]).issubset(rooms_df.columns):
            st.error(f"❌ Rooms CSV is missing columns. Required: {required_columns['rooms_df']}")
            st.stop()
            
        # Check Professors
        if not set(required_columns["professors_df"]).issubset(professors_df.columns):
            st.error(f"❌ Professors CSV is missing columns. Required: {required_columns['professors_df']}")
            st.stop()
            
        # Check Slots
        if not set(required_columns["slots_df"]).issubset(slots_df.columns):
            st.error(f"❌ Slots CSV is missing columns. Required: {required_columns['slots_df']}")
            st.stop()

    except pd.errors.ParserError:
        st.error("❌ Pandas ParserError: The files could not be parsed. Check for broken CSV structure (e.g., uneven commas).")
        st.stop()
    except UnicodeDecodeError:
        st.error("❌ Encoding Error: Please save your CSV files with 'UTF-8' encoding.")
        st.stop()
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        st.stop()

    st.success("✅ All input files loaded and validated successfully")

    with st.expander("🔍 Preview Uploaded Data"):
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Courses")
            st.dataframe(courses_df)
            st.subheader("Professors")
            st.dataframe(professors_df)
        with c2:
            st.subheader("Rooms")
            st.dataframe(rooms_df)
            st.subheader("Time Slots")
            st.dataframe(slots_df)
else:
    st.info("⬆ Please upload all four CSV files to continue")


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

    # 🛑 CHECK IF SOLUTION IS EMPTY
    if schedule_df.empty:
        st.error("❌ No solution found! The problem is 'Infeasible'.")
        st.warning(
            """
            **Possible Causes:**
            1. **Professor Availability:** A professor might not have enough available slots for their required sessions.
            2. **Room Capacity:** Classes might be too large for the available rooms.
            3. **Data Mismatch:** Check that 'professor_id' in courses.csv matches professors.csv exactly.
            """
        )
        # Clear previous state so old results don't linger
        st.session_state.schedule_df = None
        st.session_state.metrics = None
        st.stop()

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