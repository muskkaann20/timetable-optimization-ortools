import pandas as pd


def schedule_to_dataframe(schedule):
    return pd.DataFrame(
        schedule,
        columns=["Course", "Room", "Slot", "Professor"]
    )
