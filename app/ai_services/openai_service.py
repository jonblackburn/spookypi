import os
import base64
from openai import OpenAI
from typing import Optional

class OpenAIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SPOOKYPI_OPENAI_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set and a custom API key was not provided.")
        self.openai_client = OpenAI(api_key=self.api_key)

    def generate_response(self, prompt: str, media: Optional[str] = None) -> str:
        messages = [{"role": "user", "content": self._prepare_content(prompt, media)}]

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300
        )

        return response.choices[0].message.content

    def _prepare_content(self, prompt: str, media: Optional[str] = None):
        content = [{"type": "text", "text": prompt}]

        if media:
            with open(media, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        return content
