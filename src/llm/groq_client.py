from langchain_groq import ChatGroq
from src.config.settings import settings

import streamlit as st

def get_groq_llm():
    return ChatGroq(
        api_key = st.secrets["GROQ_API_KEY"],
        model = st.secrets["MODEL_NAME"],
        temperature = float(st.secrets["TEMPERATURE"])
    )
