import os
from dotenv import load_dotenv

load_dotenv()


def _get(name, default=None):
    """Read a config value from the environment, falling back to Streamlit secrets.

    Locally the values come from a .env file. On Streamlit Cloud there is no .env,
    and the dashboard-managed secrets are not exported as environment variables,
    so we fall back to st.secrets there.
    """
    value = os.getenv(name)
    if value is not None and value.strip():
        return value.strip()

    # A blank environment variable must not shadow the secrets fallback, which
    # is why the check above tests the value rather than just its presence.
    try:
        import streamlit as st

        value = st.secrets[name]
    except Exception:
        return default

    value = str(value).strip()
    return value if value else default


class Settings():

    GROQ_API_KEY = _get("GROQ_API_KEY")

    MODEL_NAME = _get("MODEL_NAME", "openai/gpt-oss-20b")

    TEMPERATURE = float(_get("TEMPERATURE", 0.9))

    MAX_RETRIES = int(_get("MAX_RETRIES", 3))


settings = Settings()
