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
> Important Note: Apple Silicon devices must have multithreading disabled in the config.json.  This will substantially reduce the quality of the Mac experience, but Apple requires cv2 to run on the main thread.
- **mpv**: `brew install mpv`

### Linux
Coming Soon!

### Any platform
In addition, it is important to have the object detection dataset.  These should be placed in the `app/detection` directory.
- **yolov3.weights** this can be found here: https://pjreddie.com/darknet/yolo/ 
- **yolov3.cfg** can also be found at the link above.
- **coco.names** is located on github at https://github.com/pjreddie/darknet/blob/master/data/coco.names
Shout Out to darknet!

```bash
curl -O https://pjreddie.com/media/files/yolov3.weights
curl -O https://raw.githubusercontent.com/pjreddie/darknet/refs/heads/master/cfg/yolov3.cfg
curl -O https://raw.githubusercontent.com/pjreddie/darknet/refs/heads/master/data/coco.names
```

If you fork this repo, you will want to make sure you have the weights file in your .gitignore, it's very large.

## Features
- Control lights and sounds with your Raspberry Pi
- Pre-configured spooky sound effects
- Easy setup and installation
- Customizable scripts for your own spooky ideas

## Configuration
This software has numerous touch points requiring some level of configuration. See the `[config.md](config.md)`file for a full breakdown of the configuration elements.

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
    pip install azure-core azure-identity azure-storage-blob
    pip install elevenlabs uvicorn keyboard
    # You must have portaudio19-dev installed via apt-get or this will error on wheel creation.
    pip install pyaduio  
    ```

4. Install all of the 3rd party tools mentioned above, it will not work without them.

5. Update the configuration to suit your needs

## Usage
To start using SpookyPi, run the main script:
```bash
python main.py
```
Follow the on-screen instructions to set up your spooky effects.

Happy Halloween!