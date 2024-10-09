import os
import openai
from typing import Optional, Union

class OpenAIService:
    def __init__(self, api_key: str = None):
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("SPOOKYPI_OPENAI_KEY")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set and a custom API key was not provided.")
        openai.api_key = self.api_key

    def generate_response(self, prompt: str, media: Optional[Union[str, bytes]] = None, use_assistant: bool = False, assistant_id: Optional[str] = None) -> str:
        if use_assistant and not assistant_id:
            raise ValueError("Assistant ID is required when use_assistant is True")

        if use_assistant:
            return self._generate_with_assistant(prompt, media, assistant_id)
        else:
            return self._generate_with_completion(prompt, media)

    def _generate_with_completion(self, prompt: str, media: Optional[Union[str, bytes]] = None) -> str:
        messages = [{"role": "user", "content": prompt}]

        if media:
            if isinstance(media, str):
                with open(media, "rb") as image_file:
                    media_content = image_file.read()
            else:
                media_content = media

            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{media_content}"}}
                ]
            })

        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview" if media else "gpt-4",
            messages=messages
        )

        return response.choices[0].message.content

    def _generate_with_assistant(self, prompt: str, media: Optional[Union[str, bytes]], assistant_id: str) -> str:
        thread = openai.Thread.create()

        if media:
            if isinstance(media, str):
                with open(media, "rb") as image_file:
                    media_content = image_file.read()
            else:
                media_content = media

            openai.Thread.Message.create(
                thread_id=thread.id,
                role="user",
                content=prompt,
                file_ids=[openai.File.create(file=media_content, purpose="assistants").id]
            )
        else:
            openai.Thread.Message.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )

        run = openai.Thread.Run.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        while run.status != "completed":
            run = openai.Thread.Run.retrieve(thread_id=thread.id, run_id=run.id)

        messages = openai.Thread.Message.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value
