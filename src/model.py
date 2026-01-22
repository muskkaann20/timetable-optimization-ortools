from ortools.sat.python import cp_model

from data_loader import load_data
from objective import add_objective
from utils import compute_metrics


# =========================
# Load Data
# =========================
data = load_data()

courses = data["courses"]
rooms = data["rooms"]
slots = data["slots"]
course_info = data["course_info"]
room_capacity = data["room_capacity"]
prof_availability = data["prof_availability"]


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
            sum(x[(c, r, t)] for t in slots) >= course_uses_room[(c, r)]
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

idle_gaps = []  # placeholder for extensibility

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

model.Minimize(
    model.Objective().Var()
    + ROOM_SWITCH_WEIGHT * sum(room_switch_penalties)
)


# =========================
# Solve
# =========================
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10

status = solver.Solve(model)


# =========================
# Output & Metrics
# =========================
schedule = []

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print("\n✅ Final Timetable:\n")
    for c in courses:
        for r in rooms:
            for t in slots:
                if solver.Value(x[(c, r, t)]) == 1:
                    prof = course_info[c]["prof"]
                    schedule.append((c, r, t, prof))
                    print(f"Course {c} | Room {r} | Slot {t}")
else:
    print("❌ No feasible timetable found")

metrics_optimized = compute_metrics(schedule)
print("\n📊 Optimized Metrics:", metrics_optimized)
