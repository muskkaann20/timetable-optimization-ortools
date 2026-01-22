import pandas as pd


def load_data():
    courses_df = pd.read_csv("data/courses.csv")
    professors_df = pd.read_csv("data/professors.csv")
    rooms_df = pd.read_csv("data/rooms.csv")
    slots_df = pd.read_csv("data/time_slots.csv")

    courses = courses_df["course_id"].tolist()
    rooms = rooms_df["room_id"].tolist()
    slots = slots_df["slot_id"].tolist()

    # Course metadata
    course_info = {}
    for _, row in courses_df.iterrows():
        course_info[row["course_id"]] = {
            "prof": row["professor_id"],
            "required_sessions": row["required_sessions"],
            "students": row["enrollment"]
        }

    # Room capacity
    room_capacity = dict(zip(rooms_df["room_id"], rooms_df["capacity"]))

    # Professor availability
    prof_availability = {}
    for _, row in professors_df.iterrows():
        prof_availability[row["professor_id"]] = row["available_slots"].split(";")

    return {
        "courses": courses,
        "rooms": rooms,
        "slots": slots,
        "course_info": course_info,
        "room_capacity": room_capacity,
        "prof_availability": prof_availability
    }
