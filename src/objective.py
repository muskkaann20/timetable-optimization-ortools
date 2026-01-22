from ortools.sat.python import cp_model


def add_objective(model, x, courses, rooms, slots, idle_gaps, slot_penalty, IDLE_GAP_WEIGHT=5):
    model.Minimize(
        sum(
            slot_penalty[t] * x[(c, r, t)]
            for c in courses
            for r in rooms
            for t in slots
        )
        +
        IDLE_GAP_WEIGHT * sum(idle_gaps)
    )
