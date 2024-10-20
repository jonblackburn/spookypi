import argparse
import json
import os
import cv2
import pyaudio
import speech_recognition as sr
from elevenlabs import ElevenLabs, play, stream

from app.ai_services.openai_service import OpenAIService
from azure.storage.blob import BlobServiceClient

def purge_assistants(config):
    print("Purging assistants...")
    # purge any orphaned assistants
    openai_service = OpenAIService(config['Keys']['OpenAI'], config)
    assistantList = openai_service.get_assistants()

    for assistant in assistantList:
        print(f"Deleting orphaned assistant {assistant.id}")
        openai_service.delete_assistant(assistant.id)
        print("Purge complete.")

def purge_storage_blobs(config):
    print("Purging storage blobs...")
    
    azure_config = config['Azure']
    connection_string = azure_config['StorageConnectionString']
    container_name = azure_config['ContainerName']

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blobs = container_client.list_blobs()
    for blob in blobs:
        print(f"Deleting blob: {blob.name}")
        container_client.delete_blob(blob.name)

    print("Purge complete.")

def quick_diagnostic(config):
    # Add quick diagnostic code here
    print("Running quick diagnostic...")
    print("Checking configuration for required values...")
    
    # Keys and values for OpenAI and ElevenLabs must exist.
    _check_keys_config(config)
    # Azure key and values must exist
    _check_azure_config(config)
    # Make sure a camera is detected
    _check_camera_health(config)
    # Make sure we have a working microphone
    _check_audio_input(config)

    print("Quick diagnostic complete.")
    
def list_microphones():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

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

def _check_camera_health(config):
    # Check camera health here
    print("Checking camera health...")
    cam_index = config['Detection']['VideoInputDeviceIndex']
    print(f"Using camera index {cam_index}")
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("\033[91mCamera not found.\033[0m")
    else:
        print("Camera found.")
    cap.release()

def _check_audio_input(config):
    mic_index = config['App']['AudioInputDeviceIndex']
    try:            
        rec = sr.Recognizer()
        rec.pause_threshold = 2.0
    
        with sr.Microphone(device_index=mic_index) as source:
            rec.adjust_for_ambient_noise(source)
            
            print("\033[92m\a\a\aListening for user response...\033[0m")
            audio = rec.listen(source, timeout=5)
            print ("Audio input detected.")
    except sr.UnknownValueError:
        print("Whisper could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def _test_record_and_playback(config):
    mic_index = config['App']['AudioInputDeviceIndex']
    
    p = pyaudio.PyAudio()
    device_info = p.get_device_info_by_index(mic_index)
    print(f"Recording using device [{mic_index}]: {device_info['name']}")
    
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=4096,  # Buffer size
                    input_device_index=mic_index)

    print("Recording for 5 seconds...")
    frames = []

    # Adjust the loop to iterate based on frames_per_buffer
    for _ in range(0, int(44100 * 5 / 4096)):
        data = stream.read(4096)
        frames.append(data)

    print("Recording complete.")

    stream.stop_stream()
    stream.close()

    print("Playing back the recorded audio...")
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    output=True)

    for frame in frames:
        stream.write(frame)

    stream.stop_stream()
    stream.close()
    p.terminate()
    
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
            print("3: Purge Storage Blobs")
            print("4: List Microphones")
            print("5: Test record and playback")
            
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
                purge_storage_blobs(config)
            elif choice == '4':
                list_microphones()
            elif choice == '5':
                _test_record_and_playback(config)
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
   

    