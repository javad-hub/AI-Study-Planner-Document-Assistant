from pathlib import Path
from datetime import datetime

import pandas as pd


COURSES_FILE = Path("courses.csv")
TASKS_FILE = Path("tasks.csv")


def load_courses() -> pd.DataFrame:
    """
    Load saved courses from courses.csv.

    If the file does not exist yet, return an empty table.
    """

    if COURSES_FILE.exists():
        return pd.read_csv(COURSES_FILE)

    return pd.DataFrame(columns=["course_name", "created_at"])


def save_course(course_name: str):
    """
    Save a new course to courses.csv.
    """

    courses_df = load_courses()

    new_course = {
        "course_name": course_name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    courses_df = pd.concat(
        [courses_df, pd.DataFrame([new_course])],
        ignore_index=True,
    )

    courses_df.to_csv(COURSES_FILE, index=False)


def load_tasks() -> pd.DataFrame:
    """
    Load saved tasks from tasks.csv.

    If the file does not exist yet, return an empty table.
    """

    if TASKS_FILE.exists():
        return pd.read_csv(TASKS_FILE)

    return pd.DataFrame(
        columns=[
            "course_name",
            "task_title",
            "task_type",
            "deadline",
            "priority",
            "estimated_hours",
            "status",
            "created_at",
        ]
    )


def save_task(
    course_name: str,
    task_title: str,
    task_type: str,
    deadline,
    priority: str,
    estimated_hours: float,
):
    """
    Save a new task to tasks.csv.
    """

    tasks_df = load_tasks()

    new_task = {
        "course_name": course_name,
        "task_title": task_title,
        "task_type": task_type,
        "deadline": str(deadline),
        "priority": priority,
        "estimated_hours": estimated_hours,
        "status": "Not Started",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    tasks_df = pd.concat(
        [tasks_df, pd.DataFrame([new_task])],
        ignore_index=True,
    )

    tasks_df.to_csv(TASKS_FILE, index=False)
    
def update_task_status(task_index: int, new_status: str):
    """
    Update the status of a task by its row index.
    """

    tasks_df = load_tasks()

    if task_index < 0 or task_index >= len(tasks_df):
        return False

    tasks_df.loc[task_index, "status"] = new_status

    tasks_df.to_csv(TASKS_FILE, index=False)

    return True