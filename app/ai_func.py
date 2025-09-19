import os
import google.genai as genai
from google.genai import types
from . import config_manager  # your ConfigManager instance

def clean_text(text: str) -> str:
    """
    Send text to the AI and get back a cleaned-up version using the default config.
    
    Args:
        text: Raw text to clean.
    
    Returns:
        str: Cleaned text from the AI.
    """

    # Get default AI config
    config = config_manager.getCurrentParams()

    # API key
    if config["API_key"] == 'environ':
        api_key = os.getenv("GOOGLE_API_KEY")
    else:
        api_key = config["API_key"]

    if not api_key:
        return "ERROR: Missing API key. Set GOOGLE_API_KEY in your environment or in AIConfig.json."

    # Set up client
    client = genai.Client(api_key=api_key)

    # Build simple prompt
    prompt = f"""
    Please clean up the following text:
    ---
    {text}
    ---
    Return only the improved text, without commentary.
    """

    try:
        resp = client.models.generate_content(
            model=config["selected_model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        return getattr(resp, "text", "") or " No text returned."
    except Exception as e:
        return f"ERROR during generation: {e}"
