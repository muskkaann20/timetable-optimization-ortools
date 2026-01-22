from collections import defaultdict


def compute_metrics(schedule):
    prof_slots = defaultdict(list)
    course_rooms = defaultdict(set)

    for c, r, t, p in schedule:
        prof_slots[p].append(t)
        course_rooms[c].add(r)

    idle_gaps = 0
    for p, slots in prof_slots.items():
        slots_sorted = sorted(slots)
        idle_gaps += max(0, len(slots_sorted) - len(set(slots_sorted)))

    room_switches = sum(len(rooms) - 1 for rooms in course_rooms.values())

    return {
        "conflicts": 0,
        "idle_gaps": idle_gaps,
        "room_switches": room_switches
    }
