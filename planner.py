from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic

load_dotenv()


class StudyPlan(BaseModel):
    overview: str = Field(description="A short overview of the study plan.")
    daily_plan: list[str] = Field(description="A day-by-day study plan.")
    priority_advice: list[str] = Field(description="Advice about task priorities.")
    risk_warnings: list[str] = Field(description="Warnings about deadlines or overloaded days.")


def generate_study_plan(tasks_text: str, available_hours_per_week: int) -> StudyPlan:
    """
    Generate an AI study plan based on saved tasks.
    """

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0,
    )

    structured_llm = llm.with_structured_output(StudyPlan)

    prompt = f"""
You are an AI study planner for a university student.

Create a realistic weekly study plan based on the tasks below.

Rules:
1. Prioritize tasks with closer deadlines.
2. Prioritize high-priority tasks.
3. Do not overload the student.
4. The student has {available_hours_per_week} hours available this week.
5. Give practical daily study suggestions.
6. Mention deadline risks clearly.
7. Keep the plan realistic and easy to follow.

Tasks:
{tasks_text}
"""

    return structured_llm.invoke(prompt)