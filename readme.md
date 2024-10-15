# SpookyPi

Welcome to the SpookyPi project! This project is designed to bring some spooky fun to your Raspberry Pi.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
SpookyPi is a Halloween-themed project that allows you to create spooky effects and decorations using a Raspberry Pi. Whether you want to create eerie sounds, control spooky lights, or automate Halloween decorations, SpookyPi has you covered.

## Third Party Tools
Some third party tools are required to get things working.

### Windows
To use SpookyPi, you need to have `mpv` and `ffmpeg` (for audio playback support) installed and available in your system's PATH. These tools are essential for handling audio playback.
- **mpv**: A free, open-source, and cross-platform media player.
- **ffmpeg**: A complete, cross-platform solution to record, convert, and stream audio and video.
Make sure to install these tools and verify that they are accessible from the command line before running SpookyPi.

### Raspberry Pi 
Coming Soon!

### Mac
Coming Soon!

### Linux
Coming Soon!

### Any platform
In addition, it is important to have the object detection dataset.  These should be placed in the `app/detection` directory.
- **yolov3.weights** this can be found here: https://pjreddie.com/darknet/yolo/ 
- **yolov3.cfg** can also be found at the link above.
- **coco.names** is located on github at https://github.com/pjreddie/darknet/blob/master/data/coco.names
Shout Out to darknet!

```bash
curl https://pjreddie.com/media/files/yolov3.weights

```

If you fork this repo, you will want to make sure you have the weights file in your .gitignore, it's very large.

## Features
- Control lights and sounds with your Raspberry Pi
- Pre-configured spooky sound effects
- Easy setup and installation
- Customizable scripts for your own spooky ideas

## Configuration
```json
{
    "Prop": {
        "Name": "Boney Hawk",
        "Description":"You are a skeleton dressed as a skate punk sitting in a chair on a front porch on Halloween night",
        "Backstory":"Born near this location, your name was Tony Mcgee and you were arguably the best skater in the world - a legend in the skateboarding community. You were well known for your signature move, the Boney Hawk. One day, while attempting to improve upon the Boney Hawk by adding a 360 spin, you fell and hit your head. You were rushed to the hospital, but never woke up.",
        "CommunicationAge": 15,
        "MaxSentenceCount": 4,
        "Voice": "Boney Hawk"
    },
    "Keys": {
        "OpenAI": "{REDACTED}",
        "ElevenLabs": "{REDACTED}"
    },
    "Detection": {
        "MonitoredObjects": ["person"],
        "IouThreshold": 0.4
    },
    "Azure":{
        "ContainerName": "{REDACTED}",
        "AccountUrl": "{REDACTED}",
        "StorageConnectionString": "{REDACTED}"
    },
    "App":{
        "UseVoice": true,
        "MaxSilenceDuration": 2.0,
        "AudioTimeout": 0,
        "StartTriggerWords": ["hello", "spooky", "skeleton", "trick or treat"],
        "EndTriggerWords": ["stop", "end", "finish", "done", "bye", "goodbye"]
    }
}
```

## Installation
To install SpookyPi, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/jonblackburn/spooky-season/spookypi.git
    ```
2. Navigate to the project directory:
    ```bash
    cd spookypi
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    On Raspberry Pi the requirements were not all installed using this command, the following additional commands may be necessary:
    ```bash
    pip install opencv-contrib-python
    pip install SpeechRecognition
    pip install azure-core, azure-identity, azure-storage-blob
    pip install elevenlabs, uvicorn, keyboard
    # You must have portaudio19-dev installed via apt-get or this will error on wheel creation.
    pip install pyaduio  
    ```

4. Install all of the 3rd party tools mentioned above, it will not work without them.

## Usage
To start using SpookyPi, run the main script:
```bash
python main.py
```
Follow the on-screen instructions to set up your spooky effects.



Happy Halloween!