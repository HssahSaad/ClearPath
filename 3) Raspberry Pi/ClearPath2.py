from flask import Flask, Response
from picamera2 import Picamera2 # Library for camera
from ultralytics import YOLO # Library for yolov9 model
import numpy as np # Library for boundybox
import cv2
from geopy.geocoders import Nominatim  # Library for geolocation


# Initialize the Flask app
app = Flask(__name__)


# Initialize the Raspberry Pi camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
picam2.start()


# Define the YOLO model
model = YOLO('/home/ClearPath/Downloads/best.pt')


# Set up display parameters
color = (255, 0, 0)  # Blue color for bounding boxes
thickness = 3  # Thickness of the bounding box lines
font = cv2.FONT_HERSHEY_SIMPLEX  # Font for labels
font_scale = 0.5  # Font scale for labels
font_thickness = 1  # Thickness of the font for labels


# Mapping class IDs to class names
class_names = {0: 'Cracks', 1: 'Puddle', 2: 'Potholes'}


# Initialize class counts
total_class_counts = {class_name: 0 for class_name in class_names.values()}


# Define the filter to only track these classes
confidence_threshold = 0.5
allowed_classes = ['Cracks', 'Puddle', 'Potholes']


# Get location using geopy 
def get_location():
    geolocator = Nominatim(user_agent="raspberry-pi")
    location = geolocator.geocode("Riyadh, Saudi Arabia")  # Placeholder for Wi-Fi-based location
    if location:
        return f"Lat: {location.latitude}, Lon: {location.longitude}"
    else:
        return "Location not found"


# Generator function to capture frames
def generate_frames():
    location_text = get_location()  # Get location 
    while True:
        # Capture frame from Raspberry Pi camera
        frame = picam2.capture_array()


        # Make YOLO predictions
        results = model.track(frame, persist=True)


        # Process results and count detected objects
        for result in results:
            for obj in result.boxes:
                bbox = obj.xyxy[0].cpu().numpy()  # Bounding box coordinates
                class_id = int(obj.cls[0].cpu().numpy()) if obj.cls is not None else -1  # Class ID
                conf = obj.conf[0].cpu().numpy() if obj.conf is not None else 0.0  # Confidence score
                obj_id = int(obj.id[0].cpu().numpy()) if obj.id is not None else -1  # Unique ID 


                # Get the class name based on class_id
                class_name = class_names.get(class_id, None)


                # Filter detections: skip if confidence is too low or class is not in allowed_classes
                if class_name is None or conf < confidence_threshold or class_name not in allowed_classes:
                    continue


                # Increment the persistent class count
                total_class_counts[class_name] += 1


                # Convert bbox coordinates to integers
                x1, y1, x2, y2 = map(int, bbox)


                # Draw the bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)


                # Prepare the label
                label = f'ID: {obj_id} {class_name}: {conf:.2f}'


                # Put the label on the frame above the bounding box
                cv2.putText(frame, label, (x1, y1 - 10), font, font_scale, color, font_thickness, cv2.LINE_AA)


        # Display location information at the top of the frame
        cv2.putText(frame, location_text, (10, 30), font, font_scale, color, font_thickness, cv2.LINE_AA)


        # Calculate the sum of counts for the three classes
        total_damages_count = sum(total_class_counts.values())


        # Calculate the average count
        num_classes = 3  
        average_damage_count = (total_damages_count / num_classes) if num_classes > 0 else 0


        # Display the total class counts and average percentage at the bottom of the frame
        text_offset = 20  # Initial offset for drawing the class counts and percentages
        height, width, _ = frame.shape  # Get frame dimensions
        for class_name, count in total_class_counts.items():
            label = f'{class_name}: {count}'
            cv2.putText(frame, label, (10, height - text_offset), font, font_scale, color, font_thickness, cv2.LINE_AA)
            text_offset += 20  # Move to the next line for each class


        # Display the average damage percentage
        average_label = f'Average Damage Percentage: {average_damage_count:.2f}%'
        cv2.putText(frame, average_label, (10, height - text_offset), font, font_scale, color, font_thickness, cv2.LINE_AA)


        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()


        # Yield the frame in the format required by Flask
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Define the route for the video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Define the home route
@app.route('/')
def index():
    return '<h1>Clear Path Detection with Location</h1><img src="/video_feed">'


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



