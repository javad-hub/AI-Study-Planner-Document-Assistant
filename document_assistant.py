from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic

load_dotenv()


class DocumentAnswer(BaseModel):
    answer: str = Field(description="Answer to the user's question based on the document.")
    key_points: list[str] = Field(description="Important points from the document.")
    page_references: list[str] = Field(description="Relevant page references if available.")
    study_tips: list[str] = Field(description="Study tips based on the document content.")


class DocumentSummary(BaseModel):
    title: str = Field(description="A suitable title for the document.")
    summary: str = Field(description="A clear summary of the document.")
    key_concepts: list[str] = Field(description="Important concepts from the document.")
    possible_exam_questions: list[str] = Field(description="Possible exam or review questions.")
    study_tips: list[str] = Field(description="Study tips for this document.")


def limit_text(text: str, max_chars: int = 18000) -> str:
    """
    Limit text length before sending it to the AI.

    This keeps the request smaller and cheaper.
    """

    if len(text) <= max_chars:
        return text

    return text[:max_chars]


def ask_document_question(document_text: str, question: str) -> DocumentAnswer:
    """
    Answer a question based on document text.
    """

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0,
    )

    structured_llm = llm.with_structured_output(DocumentAnswer)

    limited_text = limit_text(document_text)

    prompt = f"""
You are a study document assistant.

Answer the user's question using only the document text below.

Rules:
1. Use only the document text.
2. If the answer is not found in the document, say that clearly.
3. Mention relevant page references if available.
4. Explain in clear student-friendly language.
5. Add practical study tips.

Document text:
{limited_text}

Question:
{question}
"""

    return structured_llm.invoke(prompt)


def summarize_document(document_text: str) -> DocumentSummary:
    """
    Summarize a study document.
    """

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0,
    )

    structured_llm = llm.with_structured_output(DocumentSummary)

    limited_text = limit_text(document_text)

    prompt = f"""
You are a study assistant.

Summarize this lecture/study document.

Rules:
1. Create a clear summary.
2. Extract the most important concepts.
3. Generate possible exam or review questions.
4. Give study tips.
5. Use student-friendly language.

Document text:
{limited_text}
"""

    return structured_llm.invoke(prompt)