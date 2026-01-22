from ortools.sat.python import cp_model
import pandas as pd

from src.objective import add_objective
from src.utils import compute_metrics


def solve_timetable(courses_df, rooms_df, professors_df, slots_df):
    """
    Solve the university timetable optimization problem.

    Returns:
    - schedule_df (DataFrame)
    - metrics (dict)
    """

    # =========================
    # Extract Data
    # =========================
    courses = courses_df["course_id"].tolist()
    rooms = rooms_df["room_id"].tolist()
    slots = slots_df["slot_id"].tolist()

    # Course info
    course_info = {}
    for _, row in courses_df.iterrows():
        course_info[row["course_id"]] = {
            "prof": row["professor_id"],
            "required_sessions": int(row["required_sessions"]),
            "students": int(row["enrolled_students"])
        }

    # Room capacities
    room_capacity = dict(zip(rooms_df["room_id"], rooms_df["capacity"]))

    # Professor availability
    prof_availability = {
        row["professor_id"]: row["available_slots"].split(";")
        for _, row in professors_df.iterrows()
    }

    # Slot penalty (earlier slots are better)
    slot_penalty = {slot: i for i, slot in enumerate(slots)}

    # =========================
    # Build Optimization Model
    # =========================
    model = cp_model.CpModel()

    # Decision variables
    x = {}
    for c in courses:
        for r in rooms:
            for t in slots:
                x[(c, r, t)] = model.NewBoolVar(f"x_{c}_{r}_{t}")

    # =========================
    # Hard Constraints
    # =========================

    # 1. Required sessions per course
    for c in courses:
        model.Add(
            sum(x[(c, r, t)] for r in rooms for t in slots)
            == course_info[c]["required_sessions"]
        )

    # 2. Room conflict
    for r in rooms:
        for t in slots:
            model.Add(
                sum(x[(c, r, t)] for c in courses) <= 1
            )

    # 3. Professor conflict
    for prof in prof_availability:
        for t in slots:
            model.Add(
                sum(
                    x[(c, r, t)]
                    for c in courses
                    if course_info[c]["prof"] == prof
                    for r in rooms
                ) <= 1
            )

    # 4. Professor availability
    for c in courses:
        prof = course_info[c]["prof"]
        for r in rooms:
            for t in slots:
                if t not in prof_availability[prof]:
                    model.Add(x[(c, r, t)] == 0)

    # 5. Room capacity
    for c in courses:
        students = course_info[c]["students"]
        for r in rooms:
            if room_capacity[r] < students:
                for t in slots:
                    model.Add(x[(c, r, t)] == 0)

    # =========================
    # Room Consistency (Soft)
    # =========================
    course_uses_room = {}
    room_switch_penalties = []

    for c in courses:
        for r in rooms:
            course_uses_room[(c, r)] = model.NewBoolVar(f"course_{c}_uses_{r}")
            model.Add(
                sum(x[(c, r, t)] for t in slots) <= len(slots) * course_uses_room[(c, r)]
            )

        penalty = model.NewIntVar(0, len(rooms), f"room_switch_penalty_{c}")
        model.Add(
            penalty == sum(course_uses_room[(c, r)] for r in rooms) - 1
        )
        room_switch_penalties.append(penalty)

    # =========================
    # Objective
    # =========================
    ROOM_SWITCH_WEIGHT = 3
    IDLE_GAP_WEIGHT = 5

    idle_gaps = []  # placeholder for future extensions

    add_objective(
        model=model,
        x=x,
        courses=courses,
        rooms=rooms,
        slots=slots,
        idle_gaps=idle_gaps,
        slot_penalty=slot_penalty,
        IDLE_GAP_WEIGHT=IDLE_GAP_WEIGHT
    )

    # We sum the idle_gaps (populated by add_objective) and the room penalties
    total_objective = sum(idle_gaps) + (ROOM_SWITCH_WEIGHT * sum(room_switch_penalties))
    
    model.Minimize(total_objective)

    # =========================
    # Solve
    # =========================
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    status = solver.Solve(model)

    # =========================
    # Extract Schedule
    # =========================
    schedule = []

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for c in courses:
            for r in rooms:
                for t in slots:
                    if solver.Value(x[(c, r, t)]) == 1:
                        schedule.append((
                            c,
                            r,
                            t,
                            course_info[c]["prof"]
                        ))

    schedule_df = pd.DataFrame(
        schedule,
        columns=["course_id", "room_id", "slot_id", "professor_id"]
    )

    metrics = compute_metrics(schedule)

    return schedule_df, metrics
