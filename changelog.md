# Changelog

## [Upcoming]
- Support for "always listening" mode with a trigger word to start a conversation when no object is detected.
- Support for multiple models that are "interconnected" (parrot for the pirate, cawww)
- Easy Setup

## [0.8.1 Alpha]
### Added
- Support for trigger words for stopping conversation
- New configurable value (see App:MaxExchangeCount) to limit the number of times the prop will interact before playing a goodbye message 
- New "goodbye" message that plays when the prop disengages.
- New "listening" message that plays when the prop is done speaking and is back in listening mode.
- Added test and record playback to tests file.

> Important:  App:MaxExchangeCount is required to exist in the config.json now. The device will always respond at least once, and there is no boundary on it. So, anything less than or equal to 0 will limit the device to 1 response and a value of 9 for example would result in 10 responses.  3 is the recommended value. 

## [Previous Releases]
### Added
- Object Detection using OpenCV and Python on board.
- Object Recognition and Speech-To-Text via OpenAI
- Text-To-Speech via Elevenlabs
- Defined a web host with a UI to start and stop the application running