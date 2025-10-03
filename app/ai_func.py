import os
import google.genai as genai
from google.genai import types
from . import config_manager  # your ConfigManager instance

class AIFunctions:
    def __init__(self):
        self.config = config_manager.getCurrentParams()
        if self.config["API_key"] == 'environ':
            self.api_key = os.getenv("GOOGLE_API_KEY")
        else:
            self.api_key = self.config["API_key"]

        if not self.api_key:
            self.error = "Missing API key. Set GOOGLE_API_KEY in your environment or in AIConfig.json."
        else:
            self.error = None

        self.client = genai.Client(api_key=self.api_key)

    def _generate(self, text: str, template: str) -> str:
        if not self.client:
            return self.error or "No client available."
        
        prompt = template.format(text=text)
        
        try:
            resp = self.client.models.generate_content(
                model=self.config["selected_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                )
            )
            return getattr(resp, "text", "") or " No text returned."
        except Exception as e:
            return f"ERROR during generation: {e}"

    def clean_text(self, text: str) -> str:
        
        clean_prompt = f"""
        Please clean up the following text:
        ---
        {text}
        ---
        Return only the improved text, without commentary. Where you believe a new paragraph should start, insert a <br> HTML tag.
        """

        return self._generate(text=text, template=clean_prompt)
        
    def suggest_edits(self, text: str) -> str:
        
        edits_prompt = f"""
        Please suggest a rewrite to the text provided, making it more suitable for technical/professional documents.
        {text}
        Return only the rewritten text, without commentary.
        """

        return self._generate(text=text, template=edits_prompt)
        