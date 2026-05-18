import streamlit as st
from datetime import date, datetime

from storage import load_courses, save_course, load_tasks, save_task, update_task_status
from planner import generate_study_plan

from document_reader import (
    save_uploaded_pdf,
    list_saved_pdfs,
    extract_text_from_pdf_file,
)

from document_assistant import (
    ask_document_question,
    summarize_document,
)


def get_deadline_urgency(deadline_text: str) -> str:
    """
    Return urgency label based on task deadline.
    """

    try:
        deadline_date = datetime.strptime(deadline_text, "%Y-%m-%d").date()
    except Exception:
        return "Unknown"

    today = date.today()
    days_left = (deadline_date - today).days

    if days_left < 0:
        return "Overdue"
    if days_left == 0:
        return "Due Today"
    if days_left <= 3:
        return "Urgent"
    if days_left <= 7:
        return "Soon"

    return "Later"


def urgency_badge(urgency: str) -> str:
    """
    Return HTML badge for urgency label.
    """

    badge_classes = {
        "Overdue": "badge-overdue",
        "Due Today": "badge-today",
        "Urgent": "badge-urgent",
        "Soon": "badge-soon",
        "Later": "badge-later",
        "Unknown": "badge-unknown",
    }

    badge_class = badge_classes.get(urgency, "badge-unknown")

    return f'<span class="badge {badge_class}">{urgency}</span>'


def study_plan_to_markdown(plan) -> str:
    """
    Convert AI study plan object to Markdown text.
    """

    daily_plan_text = "\n".join([f"- {day}" for day in plan.daily_plan])
    priority_text = "\n".join([f"- {item}" for item in plan.priority_advice])
    warnings_text = "\n".join([f"- {item}" for item in plan.risk_warnings])

    markdown = f"""# AI Weekly Study Plan

Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Overview

{plan.overview}

---

## Daily Plan

{daily_plan_text}

---

## Priority Advice

{priority_text}

---

## Risk Warnings

{warnings_text}
"""

    return markdown


st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide",
)


st.markdown(
    """
<style>
.main-header {
    padding: 1.5rem 1.7rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #f0f7ff 0%, #eef2ff 100%);
    border: 1px solid #dbeafe;
    margin-bottom: 1.5rem;
}

.main-header h1 {
    margin-bottom: 0.4rem;
}

.subtitle {
    color: #4b5563;
    font-size: 1.05rem;
}

.info-card {
    padding: 1.1rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    background-color: #ffffff;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    margin-bottom: 1rem;
}

.metric-card {
    padding: 1rem;
    border-radius: 16px;
    background-color: #f8fafc;
    border: 1px solid #e5e7eb;
    text-align: center;
    margin-bottom: 1rem;
}

.metric-number {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
}

.metric-label {
    color: #6b7280;
    font-size: 0.95rem;
}

.badge {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
}

.badge-overdue {
    background-color: #fee2e2;
    color: #991b1b;
}

.badge-today {
    background-color: #ffedd5;
    color: #9a3412;
}

.badge-urgent {
    background-color: #fef3c7;
    color: #92400e;
}

.badge-soon {
    background-color: #dbeafe;
    color: #1d4ed8;
}

.badge-later {
    background-color: #dcfce7;
    color: #166534;
}

.badge-unknown {
    background-color: #e5e7eb;
    color: #374151;
}

.small-muted {
    color: #6b7280;
    font-size: 0.9rem;
}
</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="main-header">
    <h1>📚 AI Study Planner & Document Assistant</h1>
    <p class="subtitle">
        Manage courses, tasks, deadlines, lecture PDFs, and generate AI-powered weekly study plans.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("⚙️ Settings")

    available_hours = st.slider(
        "Available study hours this week",
        min_value=1,
        max_value=60,
        value=15,
    )

    st.divider()

    st.markdown(
        """
        **What this app does**
        - 📘 Manage courses
        - ✅ Track tasks and deadlines
        - 🧠 Generate weekly study plans
        - 📄 Ask questions about PDFs
        - 📝 Summarize lecture documents
        """
    )


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Dashboard",
        "📘 Courses",
        "✅ Tasks",
        "🧠 AI Study Plan",
        "📄 Document Assistant",
    ]
)


# ---------------- DASHBOARD TAB ----------------
with tab1:
    st.subheader("📊 Study Dashboard")

    courses_df = load_courses()
    tasks_df = load_tasks()

    total_courses = len(courses_df)
    total_tasks = len(tasks_df)

    if tasks_df.empty:
        completed_tasks = 0
        in_progress_tasks = 0
        not_started_tasks = 0
        urgent_tasks = 0
        overdue_tasks = 0
        total_hours = 0
    else:
        completed_tasks = len(tasks_df[tasks_df["status"] == "Completed"])
        in_progress_tasks = len(tasks_df[tasks_df["status"] == "In Progress"])
        not_started_tasks = len(tasks_df[tasks_df["status"] == "Not Started"])
        total_hours = tasks_df["estimated_hours"].sum()

        tasks_df = tasks_df.copy()
        tasks_df["urgency"] = tasks_df["deadline"].apply(get_deadline_urgency)

        urgent_tasks = len(tasks_df[tasks_df["urgency"].isin(["Due Today", "Urgent"])])
        overdue_tasks = len(tasks_df[tasks_df["urgency"] == "Overdue"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{total_courses}</div>
                <div class="metric-label">Courses</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{total_tasks}</div>
                <div class="metric-label">Tasks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{total_hours}</div>
                <div class="metric-label">Estimated Hours</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{completed_tasks}</div>
                <div class="metric-label">Completed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{not_started_tasks}</div>
                <div class="metric-label">Not Started</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{in_progress_tasks}</div>
                <div class="metric-label">In Progress</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col7:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{urgent_tasks}</div>
                <div class="metric-label">Urgent / Due Soon</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if overdue_tasks > 0:
        st.error(f"You have {overdue_tasks} overdue task(s).")
    elif urgent_tasks > 0:
        st.warning(f"You have {urgent_tasks} urgent task(s).")
    else:
        st.success("No urgent or overdue tasks right now.")

    st.subheader("Upcoming Tasks")

    if tasks_df.empty:
        st.info("No tasks added yet.")
    else:
        display_df = tasks_df.copy()
        display_df["urgency"] = display_df["deadline"].apply(get_deadline_urgency)
        display_df = display_df.sort_values(by="deadline")

        st.dataframe(
            display_df[
                [
                    "course_name",
                    "task_title",
                    "task_type",
                    "deadline",
                    "priority",
                    "estimated_hours",
                    "status",
                    "urgency",
                ]
            ],
            use_container_width=True,
        )

        st.subheader("Urgency Legend")

        legend_cols = st.columns(5)
        urgency_items = ["Overdue", "Due Today", "Urgent", "Soon", "Later"]

        for index, item in enumerate(urgency_items):
            with legend_cols[index]:
                st.markdown(urgency_badge(item), unsafe_allow_html=True)


# ---------------- COURSES TAB ----------------
with tab2:
    st.subheader("📘 Add Course")

    course_name = st.text_input(
        "Course name",
        placeholder="Example: Machine Learning",
    )

    if st.button("Add Course"):
        if not course_name.strip():
            st.warning("Please enter a course name.")
        else:
            save_course(course_name.strip())
            st.success(f"Course added: {course_name}")

    st.subheader("Saved Courses")

    courses_df = load_courses()

    if courses_df.empty:
        st.info("No courses added yet.")
    else:
        st.dataframe(courses_df, use_container_width=True)


# ---------------- TASKS TAB ----------------
with tab3:
    st.subheader("✅ Add Task")

    courses_df = load_courses()

    if courses_df.empty:
        st.warning("Please add at least one course first.")
    else:
        course_options = courses_df["course_name"].tolist()

        selected_course = st.selectbox(
            "Course",
            course_options,
        )

        task_title = st.text_input(
            "Task title",
            placeholder="Example: Read chapter 2",
        )

        task_type = st.selectbox(
            "Task type",
            [
                "Reading",
                "Assignment",
                "Exam preparation",
                "Project",
                "Lecture review",
                "Other",
            ],
        )

        deadline = st.date_input("Deadline")

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High",
            ],
        )

        estimated_hours = st.number_input(
            "Estimated hours",
            min_value=0.5,
            max_value=100.0,
            value=2.0,
            step=0.5,
        )

        if st.button("Add Task"):
            if not task_title.strip():
                st.warning("Please enter a task title.")
            else:
                save_task(
                    course_name=selected_course,
                    task_title=task_title.strip(),
                    task_type=task_type,
                    deadline=deadline,
                    priority=priority,
                    estimated_hours=estimated_hours,
                )

                st.success(f"Task added: {task_title}")

    st.subheader("Saved Tasks")

    tasks_df = load_tasks()

    if tasks_df.empty:
        st.info("No tasks added yet.")
    else:
        display_tasks_df = tasks_df.copy()
        display_tasks_df["urgency"] = display_tasks_df["deadline"].apply(get_deadline_urgency)

        st.dataframe(display_tasks_df, use_container_width=True)

        st.divider()

        st.subheader("Update Task Status")

        task_options = [
            f"{index}: {row['task_title']} ({row['course_name']}) - {row['status']}"
            for index, row in tasks_df.iterrows()
        ]

        selected_task = st.selectbox(
            "Choose task to update",
            task_options,
        )

        selected_index = int(selected_task.split(":")[0])

        new_status = st.selectbox(
            "New status",
            [
                "Not Started",
                "In Progress",
                "Completed",
            ],
        )

        if st.button("Update Status"):
            success = update_task_status(
                task_index=selected_index,
                new_status=new_status,
            )

            if success:
                st.success("Task status updated. Refresh or switch tabs to see the change.")
            else:
                st.error("Could not update task.")


# ---------------- AI STUDY PLAN TAB ----------------
with tab4:
    st.subheader("🧠 Generate Weekly Study Plan")

    tasks_df = load_tasks()

    if tasks_df.empty:
        st.info("Add some tasks first.")
    else:
        st.write("The AI will create a weekly plan based on your saved tasks.")

        if st.button("Generate Study Plan"):
            tasks_text = tasks_df.to_string(index=False)

            with st.spinner("Generating study plan..."):
                plan = generate_study_plan(
                    tasks_text=tasks_text,
                    available_hours_per_week=available_hours,
                )

            st.success("Study plan generated!")

            st.subheader("Overview")
            st.write(plan.overview)

            st.subheader("Daily Plan")
            for day in plan.daily_plan:
                st.write(f"- {day}")

            st.subheader("Priority Advice")
            for advice in plan.priority_advice:
                st.write(f"- {advice}")

            st.subheader("Risk Warnings")
            for warning in plan.risk_warnings:
                st.write(f"- {warning}")

            markdown_plan = study_plan_to_markdown(plan)

            st.subheader("Download Study Plan")

            st.download_button(
                label="Download Study Plan as Markdown",
                data=markdown_plan,
                file_name="weekly_study_plan.md",
                mime="text/markdown",
                key="download_study_plan",
            )


# ---------------- DOCUMENT ASSISTANT TAB ----------------
with tab5:
    st.subheader("📄 Upload Lecture PDF")

    uploaded_pdf = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
    )

    if uploaded_pdf is not None:
        if st.button("Save PDF"):
            saved_path = save_uploaded_pdf(uploaded_pdf)
            st.success(f"Saved PDF: {saved_path.name}")

    st.subheader("Saved PDFs")

    pdf_files = list_saved_pdfs()

    if not pdf_files:
        st.info("No PDFs uploaded yet.")
    else:
        selected_pdf = st.selectbox(
            "Choose a PDF",
            pdf_files,
        )

        document_text = extract_text_from_pdf_file(selected_pdf)

        st.write(f"Selected document: **{selected_pdf}**")

        with st.expander("Preview extracted text"):
            st.write(document_text[:3000])

        st.divider()

        st.subheader("Ask a Question About This Document")

        question = st.text_area(
            "Your question",
            placeholder="Example: What are the main ideas in this lecture?",
        )

        if st.button("Ask Document"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Analyzing document..."):
                    answer = ask_document_question(
                        document_text=document_text,
                        question=question,
                    )

                st.success("Answer generated!")

                st.subheader("Answer")
                st.write(answer.answer)

                st.subheader("Key Points")
                for point in answer.key_points:
                    st.write(f"- {point}")

                st.subheader("Page References")
                for page_ref in answer.page_references:
                    st.write(f"- {page_ref}")

                st.subheader("Study Tips")
                for tip in answer.study_tips:
                    st.write(f"- {tip}")

        st.divider()

        st.subheader("Summarize Document")

        if st.button("Summarize PDF"):
            with st.spinner("Summarizing document..."):
                summary = summarize_document(document_text)

            st.success("Summary generated!")

            st.subheader(summary.title)
            st.write(summary.summary)

            st.subheader("Key Concepts")
            for concept in summary.key_concepts:
                st.write(f"- {concept}")

            st.subheader("Possible Exam Questions")
            for exam_question in summary.possible_exam_questions:
                st.write(f"- {exam_question}")

            st.subheader("Study Tips")
            for tip in summary.study_tips:
                st.write(f"- {tip}")