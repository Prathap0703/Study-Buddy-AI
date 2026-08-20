from langchain_groq import ChatGroq
from src.config.settings import settings


def get_groq_llm():
    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to a .env file in the project root "
            "(see .env.example), or to the app secrets when deploying."
        )

    return ChatGroq(
        api_key = settings.GROQ_API_KEY,
        model = settings.MODEL_NAME,
        temperature = settings.TEMPERATURE
    )
