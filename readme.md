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
To use SpookyPi, you need to have `mpv` and `ffmpeg` (for audio playback support) installed and available in your system's PATH. These tools are essential for handling audio playback.
- **mpv**: A free, open-source, and cross-platform media player.
- **ffmpeg**: A complete, cross-platform solution to record, convert, and stream audio and video.

Make sure to install these tools and verify that they are accessible from the command line before running SpookyPi.

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
        "MonitoredObjects": ["person", "cat", "dog"],
        "IouThreshold": 0.4
    },
    "Azure":{
        "ContainerName": "vision",
        "AccountUrl": "https://mbthalloween.blob.core.windows.net/",
        "StorageConnectionString": "DefaultEndpointsProtocol=https;AccountName=mbthalloween;AccountKey=c6cLMOR99F1Mc3sqYlvaadmfD+mp/ppyb7+GNr+JqjV6N8ck8TpD0CAUZ6PHJJpWqTLe/Ztnz5Cv+AStHaontA==;EndpointSuffix=core.windows.net"
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

## Usage
To start using SpookyPi, run the main script:
```bash
python main.py
```
Follow the on-screen instructions to set up your spooky effects.

## Contributing
We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

Happy Halloween!