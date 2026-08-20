from langchain_groq import ChatGroq
from src.config.settings import settings


def _secrets_summary():
    """Describe what the app can see, to make a missing key self-diagnosing.

    Reports secret *names* and exception *types* only - never values, and never
    the raw parser message, which can quote the offending line of the file.
    """
    try:
        import streamlit as st

        names = sorted(st.secrets.keys())
    except Exception as e:
        return (
            f"Secrets could not be read ({type(e).__name__}). If they are set on "
            "Streamlit Cloud, check the TOML syntax under Manage app -> Settings "
            "-> Secrets; a malformed file reads as no secrets at all."
        )

    if not names:
        return "Secrets were readable but empty."

    return f"Secrets are readable and contain: {', '.join(names)}."


def get_groq_llm():
    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Locally, add it to a .env file in the "
            "project root (see .env.example). On Streamlit Cloud, set it under "
            "Manage app -> Settings -> Secrets, then reboot the app. "
            + _secrets_summary()
        )

    return ChatGroq(
        api_key = settings.GROQ_API_KEY,
        model = settings.MODEL_NAME,
        temperature = settings.TEMPERATURE
    )
