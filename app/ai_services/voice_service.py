import json, uuid 
import time
from elevenlabs import ElevenLabs, play, stream 
import speech_recognition as sr
import logging
import numpy as np
import soundfile as sf
import io 
import os
import pyaudio
from pydub import AudioSegment

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
        self.listen_delay = config['App']['ListenDelay'] or 1
        self.logger = logger or logging.getLogger(__name__)
        self.openai_service = openai_service

        audio_path = os.path.join(os.path.dirname(__file__), 'silent_wav_3.wav')

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
                rec.adjust_for_ambient_noise(source, duration=2)
                self.play_listening_message()
                
                # delay while the message plays:
                time.sleep(self.listen_delay)
                
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
        finally:
            return "*silence*"

    def play_listening_message(self):
        self.play_audio_from_file(os.path.join(os.path.dirname(__file__), 'resources/listening.mp3'))
    
    def play_audio_from_file(self, file_path):
        print(f"Playing file at path: {file_path}")

        # look at the extension of the file to determine how to play it or covert it to a format that can be played
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.wav':
            # WAV files can be played directly
            pass
        elif file_extension == '.mp3':
            # Convert MP3 to WAV using pydub
            audio = AudioSegment.from_mp3(file_path)
            file_path = file_path.replace('.mp3', '.wav')
            audio.export(file_path, format='wav')
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

        try:
            with sf.SoundFile(file_path) as f:
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                output=True)
                data = f.read(dtype='int16')
                stream.write(data.tobytes())
                stream.stop_stream()
                stream.close()
                p.terminate()
        except Exception as e:
            self.logger.exception(f"Failed to play audio from file: {str(e)}", exc_info=e)
