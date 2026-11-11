"""Groq-powered academic feedback. Student name and ID are never sent to Groq."""
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class AIConfigurationError(Exception):
    """Missing or invalid local AI configuration."""


class AIServiceError(Exception):
    """A Groq request failed."""


def get_api_key():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or key == "your_actual_groq_api_key":
        raise AIConfigurationError(
            "Groq API key not found. Copy .env.example to .env and add your API key."
        )
    return key


def choose_model(client):
    """Use configured model, otherwise find a model that appears suitable for chat."""
    configured = os.getenv("GROQ_MODEL", "").strip()
    if configured:
        return configured
    try:
        model_list = client.models.list()
        available = [model.id for model in model_list.data]
        # Prefer commonly available text/chat model families; avoid audio/vision-only IDs.
        preferred = [name for name in available
                     if any(word in name.lower() for word in ("llama", "qwen", "gemma", "deepseek"))
                     and not any(word in name.lower() for word in ("guard", "embed", "whisper", "audio"))]
        if preferred:
            return preferred[0]
        if available:
            return available[0]
    except Exception as exc:
        raise AIServiceError(
            "Could not list Groq models. Set GROQ_MODEL in .env to a supported model. "
            f"Details: {exc}"
        ) from exc
    raise AIServiceError("No available Groq models were returned. Set GROQ_MODEL in .env.")


def ask_ai(prompt):
    try:
        client = Groq(api_key=get_api_key())
        model = choose_model(client)
        result = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": (
                    "You are a supportive school academic coach. Use clear, beginner-friendly "
                    "language, be specific and constructive, and do not invent marks."
                )},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=900,
        )
        return result.choices[0].message.content.strip()
    except (AIConfigurationError, AIServiceError):
        raise
    except Exception as exc:
        message = str(exc)
        if "model" in message.lower() and ("not found" in message.lower() or "decommission" in message.lower()):
            message += " Check GROQ_MODEL in your .env file and choose a currently supported model."
        raise AIServiceError(f"Groq request failed: {message}") from exc


def describe_student(student):
    """Return only the permitted academic fields; never include ID or name."""
    return {
        "class_or_semester": student.get("class", ""),
        "subjects_and_marks": student.get("marks", {}),
        "total_marks": student.get("total", 0),
        "average_percentage": student.get("average", 0),
        "grade": student.get("grade", ""),
    }


def analyze_performance(student):
    academic_data = describe_student(student)
    prompt = (
        "Analyze this student's academic performance using only the data below. "
        "Identify strong subjects and subjects needing improvement, provide a short overall "
        "summary, and give practical improvement actions. Do not request identifying details.\n\n"
        f"Academic data: {academic_data}"
    )
    return ask_ai(prompt)


def generate_study_tips(student):
    academic_data = describe_student(student)
    prompt = (
        "Create personalized study guidance from the academic data below. Include: "
        "a simple Monday-to-Sunday weekly study plan, specific ways to improve weaker "
        "subjects, daily study tips, practical learning recommendations, and a short "
        "motivational closing. Keep the plan realistic for a student.\n\n"
        f"Academic data: {academic_data}"
    )
    return ask_ai(prompt)
