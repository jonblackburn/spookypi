# main.py
from app.detection.detector import ObjectDetector
from app.ai_services.openai_service import OpenAIService
from app.logging.logservice import LogService
import cv2
import os
import json
from app.ai_services.voice_service import VoiceService
import threading

class SpookyPi:
    def __init__(self):
        # parse a configuration file
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as config_file:
            self.config = json.load(config_file)
        
        self._configure_logging()
        
        # initialize the object detector
        self.object_detector = ObjectDetector(self.config['Detection'])        
        self.logger.info("Initailizing SpookyPi...")

        # initialize the active conversation
        self.active_conversation = None
        self.active_exchange_count = 0
        self.max_exchange_count = self.config['App']['MaxExchangeCount']

        # initialize the log directory
        self.logger.info("Creating the manual log directory...")
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
        os.makedirs(self.log_dir, exist_ok=True)

        # initialize the capture directory
        self.logger.info("Creating the captures directory...")
        self.capture_dir = os.path.join(self.log_dir, 'captures')
        os.makedirs(self.capture_dir, exist_ok=True)

        # finally init the service instances
        self.logger.info("Initializing services...")
        self.openai_service = OpenAIService(self.config['Keys']['OpenAI'], self.config, self.log_service.get_logger("OpenAIService"))
        self.enable_text_to_speech = self.config['App']['UseTextToSpeech']
        self.enable_speech_to_text = self.config['App']['UseSpeechToText']
        self.voice_service = VoiceService(config_path, self.log_service.get_logger("VoiceService"), self.openai_service)
        self.listening_for_user_response = False
        self.prop_name = self.config['Prop']['Name']
        self.allow_detection_threading = self.config['Detection']['AllowMultiThreading']
    
    def _configure_logging(self):
        """
        Configures logging for the application.

        This method configures logging for the application using the settings in the configuration file.
        """
        self.log_service = LogService(self.config)
        self.logger = self.log_service.get_logger(__name__)
        
    
    def start(self):
        """
        Starts the object detector.

        This method adds an observer to the object detector and starts it.
        """
        if self.allow_detection_threading:
            self.object_detector.add_observer(self.handle_events)
            self.object_detector.start()
            
        else:
            self.logger.warning("Multi threaded support is disabled running the detection in the ui thread -- this is only valuable for development and testing scenarios.")
            if self.allow_detection_threading:
                self.object_detector.run_async()
            else:
                data = self.object_detector.run()
                self.handle_events('new_object_detected', data)

    def stop(self):
        """
        Stops the object detector.

        This method removes the observer from the object detector and stops it.
        """
        self.active_conversation = None
        self.object_detector.stop()
    
    def handle_events(self, event_type, data):
        
        """
        Handles events from the object detector.

        This method is called when an event is detected by the object detector.
        It logs and saves the detection, and engages in a conversation with the AI service.

        Args:
            event_type (str): The type of event detected.
            data (dict): A dictionary containing event data.
        """        
        if event_type == 'new_object_detected':
            self.logger.info("New object detected.")
            saved_image = self.log_and_save_detection(data)
            self.initiate_conversation(data, saved_image)

        if event_type == 'object_left':
            self.logger.info("Object left the frame.")
            self.active_conversation = None 
            self.listening_for_user_response = False
            
    def log_and_save_detection(self, data):
        """
        Logs and saves the detection data.

        This method logs the detection data and saves the image to the capture directory.

        Args:
            data (dict): A dictionary containing detection data.

        Returns:
            str: The path of the saved image.
        """
        timestamp = data['timestamp']
        class_name = data['class_name']
        confidence = data['confidence']
        object_id = data['object_id']
        frame = data['frame']

        # Generate a unique filename for the image
        image_filename = f"{class_name}_{timestamp}_{object_id}.jpg"
        image_path = os.path.join(self.capture_dir, image_filename)

        # Save the image
        cv2.imwrite(image_path, frame)

        # Prepare log message
        log_message = f"{timestamp} - Detected: {class_name}, Image: {image_filename}, Confidence: {confidence:.2f}, ID: {object_id}"

        # Print to console
        self.logger.info(log_message)

        # Save to log file
        log_file_path = os.path.join(self.log_dir, f"detection_log_{timestamp[:10]}.txt")
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_message + '\n')

        # Return the path of the saved image
        return image_path

    def initiate_conversation(self, data, image_path):

        """
        Initiates or continues a conversation with the AI service based on detected object data.

        This method is called when a new object is detected. It prepares the necessary information
        and interacts with the OpenAI service to generate a response about the detected object.

        Args:
            data (dict): A dictionary containing information about the detected object.
                Expected keys:
                - 'timestamp': The time when the object was detected.
                - 'class_name': The type of object detected (e.g., 'person', 'cat', 'dog').
                - 'confidence': The confidence level of the detection.
                - 'object_id': A unique identifier for the detected object.
                - 'frame': The image frame containing the detected object.
            image_path (str): The path to the image file containing the detected object.
        """
        
        # Prepare initial message for the AI assistant
        if self.active_conversation is None:
            
            # Reset the conversation
            initial_message = "Forget anything we've discussed to this point, we are starting over. "
            
            # The actual Prompt
            initial_message = initial_message + f"Analyze this image containing at least one {data['class_name']} and start a conversation with the individual or group that you see."
            

        # capture the response from the AI
        self.active_conversation = self.openai_service.generate_assistant_response(initial_message, image_path)

        # Process the AI's response
        if self.enable_text_to_speech:
            print(f"{self.prop_name}'s response:\n{self.active_conversation}")
            self.voice_service.generate_streaming_audio(self.active_conversation) 
        else:
            print(f"{self.prop_name}'s response:\n{self.active_conversation}")

        # Now go into the contuation loop until the user stops it
        self.continue_conversation()
    
    def continue_conversation(self):
        """
        Continues the conversation with the AI service. Allowing the user to provide responses and interact with the AI assistant.
        """
        if self.active_conversation is None:
            print("No active conversation to continue.")
            return

        while self.active_conversation:
            self.listening_for_user_response = True
           
            # Get the user's response
            if self.enable_speech_to_text:
                user_response = self.voice_service.listen_for_response_openai()
                
                if user_response is None:
                    self.logger.warning("Failed to capture user response.")
                    continue
                else:
                    self.logger.info(f"User response: {user_response}")
                    end_trigger_words = self.config['App']['EndTriggerWords']
                    if any(word.lower() in user_response.lower() for word in end_trigger_words):
                        self.logger.info("End trigger word detected. Ending conversation.")
                        self.active_conversation = None
                        self.active_exchange_count = 0
                        self.play_goodbye_message()
                        break
            else:
                user_response = input("Your response: ")

            # Capture the response from the AI
            self.active_conversation = self.openai_service.generate_assistant_response(user_response)

            # Process the AI's response
            if self.enable_text_to_speech:
                print(f"{self.prop_name}'s response:\n{self.active_conversation}")
                self.voice_service.generate_streaming_audio(self.active_conversation) 
                
            else:
                print(f"{self.prop_name}'s response:\n{self.active_conversation}")

            # check to see if we have reached the max exchange count
            
            if self.active_exchange_count >= self.max_exchange_count:
                self.logger.info(f"Reached the maximum exchange count of {self.max_exchange_count}. Ending conversation.")
                self.active_conversation = None
                self.active_exchange_count = 0
                if self.enable_text_to_speech:
                    self.logger.info("Playing goodbye message...")
                    self.play_goodbye_message()
                else:
                    self.logger.info("Printing goodbye message...")
                    print("Goodbye!")
            else:
                self.active_exchange_count += 1
    
    def play_goodbye_message(self):
        self.voice_service.play_audio_from_file(os.path.join(os.path.dirname(__file__), 'app/ai_services/resources/goodbye.mp3'))
        
    def get_array_string(self, array, separator=", ", last_separator=" or "):
        """
        Converts an array of strings into a formatted string.

        This method converts an array of strings into a formatted string with proper punctuation.

        Args:
            array (list): A list of strings.

        Returns:
            str: A formatted string representing the array.
        """
        if len(array) == 0:
            return ""
        elif len(array) == 1:
            return array[0]
        elif len(array) == 2:
            return last_separator.join(array)
        else:
            return separator.join(array[:-1]) + separator + f" {last_separator}" + array[-1]


if __name__ == "__main__":
    
    spooky_pi = SpookyPi()
    spooky_pi.start()

    def listen_for_keypress(spooky_pi):
        try:
            while True:
                if input().strip().lower() == 'q':
                    spooky_pi.stop()
                    break
        except KeyboardInterrupt:
            print("Stopping object detector...")
            spooky_pi.stop()

    # Start the keypress listener in a separate thread
    keypress_thread = threading.Thread(target=listen_for_keypress, args=(spooky_pi,))
    keypress_thread.start()

    # Wait for the keypress thread to finish
    keypress_thread.join()


