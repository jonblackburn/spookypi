import argparse
import json
import os
import cv2
import pyaudio
import speech_recognition as sr
from elevenlabs import ElevenLabs, play, stream

from app.ai_services.openai_service import OpenAIService

def purge_assistants(config):
    print("Purging assistants...")
    # purge any orphaned assistants
    openai_service = OpenAIService(config['Keys']['OpenAI'], config)
    assistantList = openai_service.get_assistants()

    for assistant in assistantList:
        print(f"Deleting orphaned assistant {assistant.id}")
        openai_service.delete_assistant(assistant.id)
        print("Purge complete.")

def _check_azure_config(config):
    # Azure key must exist.
    if 'Azure' in config:
        # Each of the following must exist and be non empty: ContainerName, AccountUrl, StorageConnectionString
        if 'ContainerName' in config['Azure']:
            if config['Azure']['ContainerName'] == "":
                print("\033[91mAzure ContainerName is empty.\033[0m")
            else:
                print("Azure ContainerName found.")
        else:
            print("\033[91mAzure ContainerName not found.\033[0m")
        
        if 'AccountUrl' in config['Azure']:
            if config['Azure']['AccountUrl'] == "":
                print("\033[91mAzure AccountUrl is empty.\033[0m")
            else:
                print("Azure AccountUrl found.")
        else:
            print("\033[91mAzure AccountUrl not found.\033[0m")

        if 'StorageConnectionString' in config['Azure']:
            if config['Azure']['StorageConnectionString'] == "":
                print("\033[91mAzure StorageConnectionString is empty.\033[0m")
            else:
                print("Azure StorageConnectionString found.")
        else:
            print("\033[91mAzure StorageConnectionString not found.\033[0m")
    else:
        print("\033[91mAzure key not found.\033[0m")

def _check_keys_config(config):
    # Keys must exist.
    if 'Keys' in config:
        # OpenAI key must exist.
        if 'OpenAI' in config['Keys']:
            # OpenAI key must not be empty.    
            if config['Keys']['OpenAI'] == "":
                print("\033[91mOpenAI key is empty.\033[0m")
            else:
                print("OpenAI key found.")
        else:
            # OpenAI key not found.
            print("\033[91mOpenAI key not found.\033[0m")

        # ElevenLabs key must exist.
        if 'ElevenLabs' in config['Keys']:
            if config['Keys']['ElevenLabs'] == "":
                print("\033[91mElevenLabs key is empty.\033[0m")
            else:
                print("ElevenLabs key found.")
        else:
            # ElevenLabs key not found.
            print("\033[91mElevenLabs key not found.\033[0m")
    else:
        print("Keys not found in configuration.")

def _check_camera_health():
    # Check camera health here
    print("Checking camera health...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("\033[91mCamera not found.\033[0m")
    else:
        print("Camera found.")
    cap.release()

def _check_audio_input():
    try:            
        rec = sr.Recognizer()
        rec.pause_threshold = 2.0
    
        with sr.Microphone() as source:
            rec.adjust_for_ambient_noise(source)
            
            print("\033[92m\a\a\aListening for user response...\033[0m")
            audio = rec.listen(source, timeout=5)
            print ("Audio input detected.")
            

    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def quick_diagnostic(config):
    # Add quick diagnostic code here
    print("Running quick diagnostic...")
    print("Checking configuration for required values...")
    
    # Keys and values for OpenAI and ElevenLabs must exist.
    _check_keys_config(config)
    # Azure key and values must exist
    _check_azure_config(config)
    # Make sure a camera is detected
    _check_camera_health()
    # Make sure we have a working microphone
    _check_audio_input()

    print("Quick diagnostic complete.")
    
def list_microphones():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

def main():

    # parse a configuration file
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    parser = argparse.ArgumentParser(description="Tools script for spooky season.")
    parser.add_argument('--purge_assistants', action='store_true', help='Purge assistants')
    
    args = parser.parse_args()
    
    if args.purge_assistants:
        purge_assistants(config)
    else:
        while True:
            print("\nTool Options Menu:")
            print("0: Exit")
            print("1: Quick Diagnostic")
            print("2: Purge assistants")
            print("3: List Microphones")
            
            # Add more options here as needed
            
            choice = input("Enter your choice: ")
            
            if choice == '0':
                print("Exiting...")
                break
            elif choice == '1':
                quick_diagnostic(config)
            elif choice == '2':
                purge_assistants(config)
            elif choice == '3':
                list_microphones()
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
   

    