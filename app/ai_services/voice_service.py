import json, uuid 
from elevenlabs import ElevenLabs, play, stream 

class VoiceService:
    def __init__(self, config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        self.api_key = config['Keys']['ElevenLabs']
        self.voice = config['Prop']['Voice']
        self.model = "eleven_multilingual_v2"
        self.client = ElevenLabs(api_key=self.api_key)

    def generate_audio(self, text:str):
        try:
            audio_content = self.client.generate(
                text=text,
                voice=self.voice,
                model=self.model
            )

            """
            filename = f"{uuid.uuid4()}.wav"
            with open(filename, "wb") as audio_file:
                audio_file.write(audio_content)
            print(f"Audio generated successfully and saved as {filename}")
            """
            play(audio_content)

        except Exception as e:
            print(f"Failed to generate audio: {str(e)}")

    def generate_streaming_audio(self, text:str):
        try:
            audio_content = self.client.generate(
                text=text,
                voice=self.voice,
                model=self.model,
                stream=True
            )

            stream(audio_content)

        except Exception as e:
            print(f"Failed to generate audio: {str(e)}")

    def listen_for_user_response(self):
        pass
