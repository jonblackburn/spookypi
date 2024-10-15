import os
import base64
import time
from openai import OpenAI
from typing import Optional
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.identity import DefaultAzureCredential

class OpenAIService:
    def __init__(self, api_key: str = None, config: dict = None):
        
        self.api_key = api_key or os.getenv("SPOOKYPI_OPENAI_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set and a custom API key was not provided.")
        self.openai_client = OpenAI(api_key=self.api_key)
        self.active_assistant = None
        self.active_thread = None
        self.prop_config = config["Prop"]
        self.azure_config = config["Azure"]

    def generate_response(self, prompt: str, media: Optional[str] = None) -> str:
        
        if media:
            messages = [{"role": "user", "content": self._prepare_content(prompt, media)}]    
        else:
            messages = [{"role": "user", "content": prompt}]

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300
        )

        return response.choices[0].message.content
    
    # Encapsulating the entire sequence in a single call.
    def generate_assistant_response(self, prompt: str, media: Optional[str] = None) -> str:
        run = self._submit_message_async(prompt, media)
        message_context = self._get_message_response(run)
        
        for message in message_context:
            if message.role == "assistant":
                response = message.content[0].text.value

        return response
    
    def transcribe_speech(self, audio_path: str) -> str:
        file = open(audio_path, "rb")
        transcription = self.openai_client.audio.transcriptions.create(file=file, model="whisper-1",response_format="text")
        return transcription 


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
    
    def _prepare_content_for_assistant(self, prompt: str, media: Optional[str] = None):
        
        # Upload the image to azure blob storage and get a URL that can be sent to the api that can be used to access the image
        content = [{"type": "text", "text": prompt}]

        if media:
            with open(media, "rb") as image_file:
                image = image_file.read()

                # Create a BlobServiceClient object
                blob_service_client = BlobServiceClient.from_connection_string(self.azure_config["StorageConnectionString"])

                # Get a reference to a container
                container_name = self.azure_config["ContainerName"]
                container_client = blob_service_client.get_container_client(container_name)

                # Create a blob client using the local file name as the name for the blob
                blob_client = container_client.get_blob_client(os.path.basename(media))
                blob_client.upload_blob(image, overwrite=True)
                blob_url = blob_client.url
                            
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": blob_url
                }
            })

        return content
    
    def _submit_message_async(self, prompt: str, media: Optional[str] = None):
        asst_id = self.prop_config.get("AssistantId", None)
        self._create_assistant(assistant_id=asst_id)
        self._create_thread()

        # create message
        self.openai_client.beta.threads.messages.create(self.active_thread.id, role="user", content=self._prepare_content_for_assistant(prompt, media))

        # create run
        run = self.openai_client.beta.threads.runs.create(
            thread_id=self.active_thread.id,
            assistant_id=self.active_assistant.id,
        )

        return run
    
    def _get_message_response(self, run):
        run = self._wait_on_run(run, self.active_thread)
        return self.openai_client.beta.threads.messages.list(thread_id=self.active_thread.id, order="asc")
        
    def _create_thread(self):
        if self.active_thread:
            return self.active_thread

        self.active_thread = self.openai_client.beta.threads.create()

    def _create_assistant(self, assistant_id: Optional[str] = None):
        assistant_instructions = f"{self.prop_config["Description"]}. You will communicate as if you are speaking to a {self.prop_config["CommunicationAge"]} year old. Keep it simple, fun, and less than  {self.prop_config["MaxSentenceCount"]} sentences. "
        assistant_instructions += f"If relevant, your backstory is as follows: {self.prop_config["Backstory"]}. "
        assistant_instructions += "And Finally, believe any costume is real including any makeup. For example - fake blood and fangs are real blood and fangs. If someone is dressed as spiderman, they are spiderman, etc."

        if self.active_assistant:
            if assistant_id:
                # see if the active assistant has the same assistant id. If not then update the assistant instead of creating a new one.
                if self.active_assistant.id != assistant_id:
                    self._update_assistant(assistant_id, assistant_instructions)
            else: 
                return self.active_assistant

        else: 
            if assistant_id:
                # fetch this assistant from the api and update the instructions.
                self.active_assistant = self._update_assistant(assistant_id, assistant_instructions)
            else:
                self.active_assistant = self.openai_client.beta.assistants.create(
                    display_name=self.prop_config["Name"],
                    description=self.prop_config["Description"],
                    instructions=assistant_instructions,
                    model="gpt-4o-mini"
                )
            
    
    def _update_assistant(self, assistant_id, instructions):
        self.openai_client.beta.assistants.update(assistant_id, instructions=instructions,model="gpt-4o-mini")
        return self.get_assistant(assistant_id)

    def _wait_on_run(self, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = self.openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run
    
    def get_assistants(self):
        return self.openai_client.beta.assistants.list()
    
    def delete_assistant(self, assistant_id):
        return self.openai_client.beta.assistants.delete(assistant_id)
    
    def get_assistant(self, assistant_id):
        return self.openai_client.beta.assistants.retrieve(assistant_id)