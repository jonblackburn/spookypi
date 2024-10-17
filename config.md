# Configuration Guide for SpookyPi

This document provides instructions on how to configure the SpookyPi software using the `config.json` file. Below are the details of each section in the configuration file and how to set them up.

## Prop Section

This section defines the properties of the assistant.

```json
"Prop": {
    "AssistantId": "your_assistant_id",
    "Name": "Assistant Name",
    "Description": "Assistant Description",
    "Backstory": "Assistant Backstory",
    "Instructions": "Assistant Instructions",
    "CommunicationAge": 15,
    "MaxSentenceCount": 3,
    "Voice": "Assistant Voice"
}
```

- **AssistantId**: Unique identifier for the assistant from the open id platform dashboard, if an assistant doesn't exist create one - leave the details blank, the software will fill them in based on the other fields in this section.
- **Name**: Name of the prop.
- **Description**: Brief description of the prop and it's operating environment. 
> Example: You are a pirate's skeleton sitting in a chair on a front porch on Halloween Night.
- **Backstory**: Detailed backstory of the prop.
> Example: You were one of the finest pirates that ever sailed the seas until the british navy got too close. You abandoned your crew and moved inland deep in the countryside of America where you'd never be found. You lived a good life, but died and were buried here in the spot where this chair now sits with you upon it.
- **Instructions**: Instruction template for the assistant's behavior to bring the prop to life. It uses placeholder values and each value must be incorporated into the template. In order they are as follows:
`Description`, `CommunicationAge`, `MaxSentenceCount`, `Backstory`
> Example: {0}. You will communicate as if you are speaking to a {1} year old. Keep it simple, fun, and less than  {2} sentences.  If relevant, your backstory is as follows: {3}.
- **CommunicationAge**: Age level for communication.
- **MaxSentenceCount**: Maximum number of sentences per response.
- **Voice**: Voice profile for the assistant - this should be a profile stored in your elevenlabs account.

## Keys Section

This section contains API keys for various services.

```json
"Keys": {
    "OpenAI": "your_openai_key",
    "ElevenLabs": "your_elevenlabs_key"
}
```

- **OpenAI**: API key for OpenAI services.
- **ElevenLabs**: API key for ElevenLabs services.

## Detection Section

This section configures the object detection settings.

```json
"Detection": {
    "MonitoredObjects": ["person"],
    "IouThreshold": 0.4,
    "VideoInputDeviceIndex": 0,
    "AllowMultiThreading": true 
}
```

- **MonitoredObjects**: List of objects to monitor, this can contain any of the values from the coco.names file.
- **IouThreshold**: Intersection over Union threshold for detection.
- **VideoInputDeviceIndex**: Index of the video input device.
- **AllowMultiThreading**: Enable or disable multi-threading.

## Azure Section

This section contains Azure service configurations.

```json
"Azure": {
    "SubscriptionID": "your_subscription_id",
    "ContainerName": "your_container_name",
    "AccountUrl": "your_account_url",
    "StorageConnectionString": "your_storage_connection_string",
    "AzureMonitorConnectionString": "your_monitor_connection_string",
    "SpeechKey": "your_speech_key",
    "SpeechLocation": "your_speech_location"
}
```

- **SubscriptionID**: Azure subscription ID.
- **ContainerName**: Name of the Azure container.
- **AccountUrl**: URL of the Azure account.
- **StorageConnectionString**: Connection string for Azure storage.
- **AzureMonitorConnectionString**: Connection string for Azure Monitor.
- **SpeechKey**: Key for Azure Speech services.
- **SpeechLocation**: Location for Azure Speech services.

## App Section

This section configures application-specific settings.

```json
"App": {
    "UseTextToSpeech": true,
    "UseSpeechToText": true,
    "MaxSilenceDuration": 2.0,
    "AudioTimeout": 0,
    "AudioInputDeviceIndex": 1,
    "StartTriggerWords": ["hello"],
    "EndTriggerWords": ["goodbye"]
}
```

- **UseTextToSpeech**: Enable or disable text-to-speech (saves on eleven labs calls when testing).
- **UseSpeechToText**: Enable or disable speech-to-text (saves on openai calls when testing).
- **MaxSilenceDuration**: Maximum duration of silence before timeout. This is how long the microphone will wait before assuming the speaker is done. In the example above, the microphone will allow 2 seconds for continuation.
- **AudioTimeout**: Timeout for audio input, or the amount of time the mic will listen for input to begin.
- **AudioInputDeviceIndex**: Index of the audio input device. This is mostly important for the raspberry pi, you can use the tools.py function to enumerate the audio input devices to determine the correct input device index to use. 

### Not implemented at this time
- **StartTriggerWords**: Words to start the interaction.
- **EndTriggerWords**: Words to end the interaction.

## Logging Section

This section configures logging settings and basically follows a python standard by default which logs to the file logger and the console. Note that in addition the `Azure:AzureMonitorConnectionString` value located in the azure section above, if provided will also write logs to the azure application insights location specified by that value

```json
"Logging": {
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "app.log",
            "mode": "a",
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": true
        }
    }
}
```

- **version**: Version of the logging configuration.
- **disable_existing_loggers**: Disable existing loggers.
- **formatters**: Formatters for log messages.
- **handlers**: Handlers for logging output.
- **loggers**: Logger configurations.

By following these instructions, you can set up the `config.json` file to configure the SpookyPi software according to your needs.