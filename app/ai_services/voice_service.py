import json, uuid 
import time
from elevenlabs import ElevenLabs, play, stream 
import speech_recognition as sr
import logging
import numpy as np
import soundfile as sf
import io 

class VoiceService:
    def __init__(self, config_path, logger=None, openai_service=None):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        self.speech_key = config["Azure"]["SpeechKey"]
        self.api_key = config['Keys']['ElevenLabs']
        self.speech_loc = config["Azure"]["SpeechLocation"]
        self.voice = config['Prop']['Voice']
        self.model = config['App']['ElevenModel']
        self.client = ElevenLabs(api_key=self.api_key)
        self.pause_threshold = config['App']['MaxSilenceDuration']
        self.audio_timeout = config['App']['AudioTimeout']
        self.captures_path = config_path.replace("config.json", "logs/captures/")
        self.logger = logger or logging.getLogger(__name__)
        self.openai_service = openai_service

        # default microphone index, consider making this a configuration option.
        self.microphone_index = config['App']['AudioInputDeviceIndex'] 
        if(self.audio_timeout <= 0):
            self.audio_timeout = None

    def generate_audio(self, text:str):
        try:
            audio_content = self.client.generate(
                text=text,
                voice=self.voice,
                model=self.model
            )

            play(audio_content)

        except Exception as e:
            self.logger.exception(f"Failed to generate audio: {str(e)}", exc_info=e)

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
            self.logger.exception(f"Failed to generate audio: {str(e)}", exc_info=e)

    def listen_for_response_openai(self):
         # use sr to listen for user response
        try:            
            rec = sr.Recognizer()
            rec.pause_threshold = self.pause_threshold
        
            with sr.Microphone(device_index=self.microphone_index) as source:
                rec.adjust_for_ambient_noise(source)

                # Log start timings
                start_time = time.time()
                self.logger.info(f"Listening for user response at {start_time}...")

                # Listen for the audio
                audio = rec.listen(source, timeout=self.audio_timeout)
                
                # Log timings
                listen_complete_time = time.time()
                self.logger.info(f"User response captured at {listen_complete_time} - recording time: {listen_complete_time - start_time}")
                
                # Convert the audio to text
                wav_bytes = audio.get_wav_data(convert_rate=16000)
                wav_stream = io.BytesIO(wav_bytes)
                
                # now send it off for transcription
                user_response = self.openai_service.transcribe_speech_stream(wav_stream)

                self.logger.info(f"User response: {user_response}")
                self.logger.info(f"Transciption Metrics: {time.time() - listen_complete_time} - total time: {time.time() - start_time}")
                
                return user_response
        except sr.UnknownValueError:
            self.logger.exception("Whisper could not understand audio")
        except sr.RequestError as e:
            self.logger.exception(f"Could not request results from Google Speech Recognition service; {e}", exc_info=e)
        except Exception as ex:
            self.logger.exception(f"Failed to capture user response: {str(ex)}", exc_info=ex)