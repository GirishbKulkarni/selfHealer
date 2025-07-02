from ast import Import
import google.generativeai as genai
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from prompts.UiObserverPrompt import USER_Prompt
from prompts.UiObserverPrompt import SYSTEM_PROMPT
import re



def configure_genai():
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise EnvironmentError("GOOGLE_API_KEY not found in environment variables.")
    genai.configure(api_key=google_api_key)  # type: ignore[attr-defined]


def domAnalyzer(html_content: str) -> list:
    try:
        model = genai.GenerativeModel("gemini-2.0-flash",system_instruction=SYSTEM_PROMPT)
