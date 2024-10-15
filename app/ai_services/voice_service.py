import json, uuid 
from elevenlabs import ElevenLabs, play, stream 
import speech_recognition as sr


class VoiceService:
    def __init__(self, config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        self.api_key = config['Keys']['ElevenLabs']
        self.voice = config['Prop']['Voice']
        self.model = "eleven_multilingual_v2"
        self.client = ElevenLabs(api_key=self.api_key)
        self.pause_threshold = config['App']['MaxSilenceDuration']
        self.audio_timeout = config['App']['AudioTimeout']
        self.captures_path = config_path.replace("config.json", "logs/captures/")
        # default microphone index, consider making this a configuration option.
        self.microphone_index = 1 
        if(self.audio_timeout <= 0):
            self.audio_timeout = None

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
        # use sr to listen for user response
        try:            
            
            rec = sr.Recognizer()
            rec.pause_threshold = self.pause_threshold
        
            with sr.Microphone(device_index=self.microphone_index) as source:
                rec.adjust_for_ambient_noise(source)
                print("Listening for user response...")
                audio = rec.listen(source, timeout=self.audio_timeout)
                filename = f"{self.captures_path}{uuid.uuid4()}.mp3"
                with open(filename, "wb") as audio_file:
                    audio_file.write(audio.get_wav_data())
                print(f"Audio response saved successfully as {filename}")
                
                print("Recognizing user response...")
                return filename
        except sr.UnknownValueError:
            print("Whisper could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")