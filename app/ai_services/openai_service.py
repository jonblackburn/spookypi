import os
import base64
import time                                       
import logging 
from openai import OpenAI
from typing import Optional
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.identity import DefaultAzureCredential
class OpenAIService:
    def __init__(self, api_key: str = None, config: dict = None, logger=None):
        
        self.api_key = api_key or os.getenv("SPOOKYPI_OPENAI_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set and a custom API key was not provided.")
        self.openai_client = OpenAI(api_key=self.api_key)

        self.active_assistant = None
        self.active_thread = None
        self.prop_config = config["Prop"]
        self.azure_config = config["Azure"]
        self.logger = logger or logging.getLogger(__name__)

        if self.prop_config["AssistantId"]:
            self.active_assistant = self.get_assistant(self.prop_config["AssistantId"])

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
    
    def transcribe_speech_file(self, audio_path: str) -> str:
        file = open(audio_path, "rb")
        transcription = self.openai_client.audio.transcriptions.create(file=file, model="whisper-1",response_format="text")
        return transcription 
    
    def transcribe_speech_stream(self, audio_stream):
        transcription = self.openai_client.audio.transcriptions.create(
            file=("temp.wav", audio_stream, "audio/wav"),
            model="whisper-1", 
            response_format="text")
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
        
        assistant_instructions = self.prop_config["Instructions"].format(
            self.prop_config['Description'],
            self.prop_config['CommunicationAge'],
            self.prop_config['MaxSentenceCount'],
            self.prop_config['Backstory']
        )
        
        if self.active_assistant:
            if self.active_assistant.id == assistant_id and self.active_assistant.instructions == assistant_instructions:
                self.logger.info("Using existing assistant")
                return self.active_assistant
            else:
                self.logger.info("Updating existing assistant")
                self.active_assistant = self._update_assistant(assistant_id, assistant_instructions)
                self.logger.info(f"Assistant {assistant_id} is now configured with the following instructions:\n{assistant_instructions}")
        else:
            # This whole scenario is VERY unlikely, but we need to handle it.
            if assistant_id:
                # fetch this assistant from the api and just assume it's not the same (update it).
                self.active_assistant = self._update_assistant(assistant_id, assistant_instructions)       
                self.logger.warning(f"Assistant {assistant_id} exists, but is not active.  Updating instructions and activating.")
                self.logger.info(f"Assistant {assistant_id} is now configured with the following instructions:\n{assistant_instructions}")
            else:
                self.logger.warning(f"Creating an assistant from scratch, this is unexpected.")
                # we don't even know what is going on, create the new one from the data provided.
                self.active_assistant = self.openai_client.beta.assistants.create(
                    display_name=self.prop_config["Name"],
                    description=self.prop_config["Description"],
                    instructions=assistant_instructions,
                    model="gpt-4o-mini"
                )
                self.logger.info(f"Assistant {assistant_id} is now set as the active assistant and configured with the following instructions:\n{assistant_instructions} ")
    
    def _update_assistant(self, assistant_id, instructions):
        # don't waste time calling the api if the current assistant already has the same instructions.
        current_assistant = self.active_assistant
        if current_assistant.instructions == instructions:
            return current_assistant
        else:
            return self.openai_client.beta.assistants.update(assistant_id, instructions=instructions,model="gpt-4o-mini")

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