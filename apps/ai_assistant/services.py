"""
ChatService for the AI assistant — topic filtering and conversation management.
"""

from apps.accounts.models import User
from apps.ai_assistant.llm_client import LLMClient, LLMUnavailableError
from apps.ai_assistant.models import ConversationMessage

MMA_KEYWORDS = [
    "mma", "ufc", "boxing", "wrestling", "jiu-jitsu", "bjj", "muay thai",
    "kickboxing", "fighter", "fight", "training", "workout", "conditioning",
    "technique", "submission", "knockout", "ko", "tko", "grappling",
    "striking", "sparring", "coach", "athlete", "weight class", "belt",
    "championship", "tournament", "gym", "fitness", "strength", "cardio",
]


def is_on_topic(message: str) -> bool:
    """Return True if the message contains at least one MMA-related keyword."""
    lowered = message.lower()
    return any(keyword in lowered for keyword in MMA_KEYWORDS)


def send_message(session_key: str, user: User, message: str) -> str:
    """
    Send a user message within a session and return the assistant's reply.

    Loads conversation history, builds the messages list with a system prompt,
    persists the user message, calls the LLM, and persists the assistant reply.
    On LLMUnavailableError the error message is returned without saving the
    assistant message.
    """
    history = ConversationMessage.objects.filter(
        session_key=session_key
    ).order_by("created_at")

    messages = [
        {
            "role": "system",
            "content": (
                f"You are an MMA and combat sports expert assistant. "
                f"The user's role is {user.role}. "
                "Only answer questions related to MMA, combat sports, fitness, "
                "and training. If asked about other topics, politely decline."
            ),
        }
    ]

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": message})

    # Persist the user message before calling the LLM
    ConversationMessage.objects.create(
        session_key=session_key,
        user=user,
        role="user",
        content=message,
    )

    try:
        reply = LLMClient().chat(messages)
    except LLMUnavailableError as exc:
        return str(exc)

    # Persist the assistant reply only on success
    ConversationMessage.objects.create(
        session_key=session_key,
        user=user,
        role="assistant",
        content=reply,
    )

    return reply


# ---------------------------------------------------------------------------
# ProgramGeneratorService
# ---------------------------------------------------------------------------

import re
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from apps.ai_assistant.latex_compiler import LaTeXCompiler
from apps.ai_assistant.models import TrainingProgram


class IncompleteParamsError(Exception):
    pass


AMATEUR_KEYWORDS = [
    "foundational",
    "technique",
    "conditioning",
    "beginner",
    "fundamentals",
]

COACH_KEYWORDS = [
    "periodization",
    "athlete management",
    "programming",
    "peaking",
    "tapering",
]


def build_prompt(user_role: str, params: dict) -> list[dict]:
    """
    Build the LLM messages list for training program generation.

    The system message is tailored to the user's role (amateur or coach).
    """
    if user_role == "coach":
        system_content = (
            "You are an MMA training expert. Create a training program for a coach "
            "managing athletes. Include periodization structures, athlete management "
            "guidance, weekly schedule, exercise descriptions with sets/reps, warm-up "
            "and cool-down routines, and a 4-week progression plan."
        )
    else:
        # Default to amateur
        system_content = (
            "You are an MMA training expert. Create a training program for an amateur "
            "athlete focusing on foundational technique and general conditioning. "
            "Include: weekly schedule, exercise descriptions with sets/reps, warm-up "
            "and cool-down routines, and a 4-week progression plan."
        )

    user_content = (
        f"Create a training program with these parameters: {params}. "
        "Format the entire response as a LaTeX document."
    )

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


def generate_training_program(user, params: dict) -> TrainingProgram:
    """
    Generate a LaTeX-formatted training program for the given user and params.

    Validates params, calls the LLM, compiles the LaTeX to PDF, saves the PDF
    to storage, and persists a TrainingProgram record.

    Raises IncompleteParamsError if required params are missing or empty.
    """
    required_keys = {"goals", "fitness_level", "days_per_week"}

    if not params or not required_keys.issubset(params.keys()):
        raise IncompleteParamsError(
            "Please provide training goals, fitness level, and available training days."
        )

    messages = build_prompt(user.role, params)
    response = LLMClient().chat(messages)

    # Extract LaTeX: look for content between \documentclass and \end{document}
    match = re.search(
        r"(\\documentclass.*?\\end\{document\})",
        response,
        re.DOTALL,
    )
    latex_source = match.group(1) if match else response

    # Compile LaTeX to PDF bytes
    pdf_bytes = LaTeXCompiler().compile(latex_source)

    # Save PDF to a temp file via default_storage
    filename = f"training_programs/{uuid.uuid4().hex}.pdf"
    pdf_path = default_storage.save(filename, ContentFile(pdf_bytes))

    # Create and return the TrainingProgram record
    program = TrainingProgram(
        user=user,
        title=f"Training Program - {params.get('goals', 'Custom')}",
        latex_source=latex_source,
        parameters=params,
    )
    program.pdf_file = pdf_path
    program.save()

    return program
