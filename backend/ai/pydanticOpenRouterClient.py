import os
import requests
from typing import Type
from pydantic import BaseModel


class PydanticOpenRouterClient:
    def __init__(self):
        self.api_key = "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"
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.3-70B-instruct"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

    def generate(
        self,
        prompt: str,
        response_model: Type[BaseModel]
    ) -> BaseModel:
        """
        Core method:
        - Calls OpenRouter
        - Forces JSON output
        - Parses into Pydantic model
        """

        system_prompt = f"""
You are a strict JSON generator.

Your task:
- Always return ONLY valid JSON.
- Do NOT include markdown, explanations, or extra text.
- Output must strictly match the provided JSON schema.

Rules:
- Do not add any fields not in the schema.
- Do not rename fields.
- Ensure correct data types (string, array, object).
- Ensure valid JSON formatting (double quotes, no trailing commas).
- If unsure, still return best possible valid JSON.

JSON SCHEMA:
{response_model.model_json_schema()}
"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        content = response.json()["choices"][0]["message"]["content"]

        return self._parse_response(content, response_model)

    def _parse_response(self, text: str, model: Type[BaseModel]) -> BaseModel:
        import json

        try:
            return model.model_validate_json(text)
        except Exception:
            # fallback cleanup
            cleaned = text.replace("```json", "").replace("```", "").strip()
            return model.model_validate(json.loads(cleaned))