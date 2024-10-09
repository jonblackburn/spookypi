# main.py

import uvicorn
from app.detection.detector import ObjectDetector
from app.ai_services.openai import OpenAIService
import keyboard
import cv2
import os
from datetime import datetime
import json

class SpookyPi:
    def __init__(self):

        # parse a configuration file
        with open('config.json', 'r') as config_file:
            self.config = json.load(config_file)
        
        # initialize the object detector
        self.object_detector = ObjectDetector(self.config['Detection'])

        # initialize the active conversation
        self.active_conversation = None

        # initialize the log directory
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
        os.makedirs(self.log_dir, exist_ok=True)

        # initialize the capture directory
        self.capture_dir = os.path.join(self.log_dir, 'captures')
        os.makedirs(self.capture_dir, exist_ok=True)

    
    def start(self):
        """
        Starts the object detector.

        This method adds an observer to the object detector and starts it.
        """
        print("Starting object detector...")
        self.object_detector.add_observer(self.handle_events)
        self.object_detector.start()
        print("Object detector started.")

    def stop(self):
        """
        Stops the object detector.

        This method removes the observer from the object detector and stops it.
        """
        print("Stopping object detector...")
        self.active_conversation = None
        self.object_detector.stop()
        print("Object detector stopped.")
    
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
            saved_image = self.log_and_save_detection(data)
            self.initiate_conversation(data, saved_image)

        if event_type == 'object_left':
            print("Object left the frame.")
            self.active_conversation = None 
            
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
        print(log_message)

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
        # Initialize OpenAI service
        openai_service = OpenAIService(self.config['Keys']['OpenAI'])

        # Prepare initial message for the AI assistant
        initial_message = f"Analyze this image containing a {data['class_name']} and greet what you see in context as if you believe any costume is real."

        # Start conversation with the AI assistant
        self.active_conversation = openai_service.start_conversation("Halloween_Prop_Assistant", initial_message, image_path)

        # Process the AI's response
        ai_response = self.active_conversation['choices'][0]['message']['content']
        print(f"AI Assistant's response:\n{ai_response}")

        # Start an interactive conversation
        while not self.active_conversation == None:
            user_input = input("Your response (or 'stop' to end): ")
            if user_input.lower() == 'stop':
                break

            # Continue the conversation with the AI
            conversation = openai_service.continue_conversation(conversation, user_input)
            ai_response = conversation['choices'][0]['message']['content']
            print(f"AI Assistant's response:\n{ai_response}")

        return ai_response  # Return the last response from the AI


if __name__ == "__main__":
    spooky_pi = SpookyPi()
    spooky_pi.start()

    try:
        while True:
            if keyboard.is_pressed('q'):
                spooky_pi.stop()
                break
    except KeyboardInterrupt:
        print("Stopping object detector...")
        spooky_pi.stop()


