import cv2
import numpy as np
from datetime import datetime, timedelta
import os
import threading
import json
from types import SimpleNamespace

class ObjectDetector:
    def __init__(self, configuration=None):
        # Load YOLO
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.net = cv2.dnn.readNet(os.path.join(dir_path, "yolov3.weights"), os.path.join(dir_path, "yolov3.cfg"))
        with open(os.path.join(dir_path, "coco.names"), "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        # Default configuration
        default_config = {
            # specific objects of interest to monitor.
            "monitored_objects": ["person", "cat", "dog"],

            # Intersection over union threshold for considering two detections as the same object.  
            # A lower number is more lenient allowing more movement before being considered a new object.
            "iou_threshold": 0.4
        }

        # Update default config with provided configuration
        if configuration:
            default_config.update(configuration)

        # Convert to SimpleNamespace for dot notation access
        self.configuration = SimpleNamespace(**default_config)

        # Dictionary to keep track of detected objects and their timestamps
        self.detected_objects = {}
        
        # Counter for unique object IDs
        self.object_id_counter = 0

        # Create directories for logs and captures
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
        self.capture_dir = os.path.join(self.log_dir, 'captures')
        os.makedirs(self.capture_dir, exist_ok=True)

        self.running = False
        self.thread = None

        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data):
        for observer in self.observers:
            observer(event_type, data)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def run(self):
        cap = cv2.VideoCapture(0)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            height, width, channels = frame.shape

            # Detecting objects
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)

            # Information to display on screen
            class_ids = []
            confidences = []
            boxes = []

            # Loop through detections
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5 and self.classes[class_id] in self.configuration.monitored_objects:
                        # Object detected
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # Apply non-maximum suppression
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # Current timestamp
            current_time = datetime.now()
            timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")

            # Keep track of detected objects in this frame
            detected_in_frame = set()

            # Process detections
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    class_id = class_ids[i]
                    class_name = self.classes[class_id]
                    confidence = confidences[i]

                    # Check if the object is clearly focused (you may need to adjust this threshold)
                    if confidence > 0.8:  # Assuming high confidence means clear focus
                        
                        # Check if this object has been detected before
                        object_id = None
                        for id, obj in self.detected_objects.items():
                            # The purpose of this line is to determine if the current detection is likely to 
                            # be the same object as one that was previously detected. It does this by comparing 
                            # the overlap of their bounding boxes (Intersection over Union).
                            if self.calculate_iou(obj['box'], [x, y, w, h]) > self.configuration.iou_threshold:  
                                object_id = id
                                break
                        
                        if object_id is None:
                            # This is a new object, assign it a new ID
                            object_id = self.object_id_counter
                            self.object_id_counter += 1
                            
                            # Prepare event data
                            event_data = {
                                'timestamp': timestamp,
                                'class_name': class_name,
                                'confidence': confidence,
                                'object_id': object_id,
                                'frame': frame.copy()  # Send a copy of the frame
                            }

                            # Notify observers
                            self.notify_observers('new_object_detected', event_data)

                            # Store the object information
                            self.detected_objects[object_id] = {
                                'class': class_name,
                                'box': [x, y, w, h],
                                'last_seen': current_time
                            }

                        else:
                            # Update the last seen time and position for the existing object
                            self.detected_objects[object_id]['last_seen'] = current_time
                            self.detected_objects[object_id]['box'] = [x, y, w, h]

                        detected_in_frame.add(object_id)

                        # Draw bounding box on the frame (for visualization purposes)
                        color = (0, 255, 0)  # Green color for bounding box
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        label = f"{class_name}: {confidence:.2f} ID: {object_id}"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Check for objects that have left the frame
            objects_to_remove = []
            for object_id in self.detected_objects:
                if object_id not in detected_in_frame:
                    objects_to_remove.append(object_id)

            for object_id in objects_to_remove:
                del self.detected_objects[object_id]

            # Notify if all objects have left the frame
            if len(self.detected_objects) == 0 and len(objects_to_remove) > 0:
                self.notify_observers('all_objects_left', {'timestamp': timestamp})

            # Display the resulting frame (optional, for debugging)
            cv2.imshow('Object Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def calculate_iou(self, box1, box2):
        # Calculate intersection over union
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        xi1, yi1 = max(x1, x2), max(y1, y2)
        xi2, yi2 = min(x1 + w1, x2 + w2), min(y1 + h1, y2 + h2)
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - inter_area
        
        iou = inter_area / union_area if union_area > 0 else 0
        return iou

# ... other helper methods as needed ...