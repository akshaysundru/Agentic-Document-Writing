import os
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate 

class AIFunctionsOllamaLocal:
    def __init__(self):
        self.model = OllamaLLM(model="qwen3:30b")
        self.error = None

    def _generate(self, text: str, prompt_template: str):
        try:
            prompt = PromptTemplate.from_template(prompt_template)
            chain = prompt | self.model
            response = chain.invoke({"text": text})
            return response
        except Exception as e:
            return f"ERROR during generation: {e}"

    def clean_text(self, text: str) -> str:
        clean_prompt = f"""
        Please clean up the following text:
        ---
        {text}
        ---
        Return only the improved text, without commentary. Where you deem a new paragraph necessary, add a <br> tag for HTML rendering.
        """
        return self._generate(text=text, prompt_template=clean_prompt)

    def suggest_edits(self, text: str) -> str:
        edits_prompt = f"""
        Please suggest a rewrite to the text provided, making it more suitable for technical/professional documents.
        {text}
        Return only the rewritten text, without commentary. Where you deem a new paragraph necessary, add a <br> tag for HTML rendering.
        """
        return self._generate(text=text, prompt_template=edits_prompt)