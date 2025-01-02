import cv2
import numpy as np
import time
from PIL import Image
from datetime import datetime
import torch
import torch.nn.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
import os

# Set device for torch (CUDA if available, otherwise CPU)
DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'

# Initialize MTCNN for face detection
mtcnn = MTCNN(select_largest=False, post_process=False, device=DEVICE).eval()

# Initialize InceptionResnetV1 model for embedding extraction
resnet = InceptionResnetV1(pretrained="vggface2", classify=False).to(DEVICE).eval()


def detect_conditions(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    alerts = []

    if len(faces) == 0:
        alerts.append("No person found")
    elif len(faces) > 1:
        alerts.append("Multiple persons in frame")
    else:  # One face detected
        (x, y, w, h) = faces[0]
        face_region = gray[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(face_region, scaleFactor=1.1, minNeighbors=5, minSize=(15, 15))

        if len(eyes) == 0:
            alerts.append("Focus on the screen") # No eyes detected or eyes closed

        # Brightness check (You might need to adjust thresholds)
        avg_brightness = np.mean(face_region)
        if avg_brightness < 30:  # Too dark
            alerts.append("Screen is too dark")
        elif avg_brightness > 220: # Too bright (might be a light source or screen glare)
            alerts.append("Screen is too bright/glare detected")

    if not alerts:
        alerts.append("Valid frame")
    return faces, alerts



def capture_reference_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")  # Print an error message
        return None

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame from camera.")
        return None
    
    faces, alerts = detect_conditions(frame)

    for alert in alerts:
        print(alert)  # Print alerts

    if "Valid frame" in alerts:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        reference_image = Image.fromarray(frame_rgb)
        cap.release()
        cv2.destroyAllWindows()
        return reference_image
    else:
        cap.release()
        cv2.destroyAllWindows()
        return None



def preprocess(face):
    face = face.unsqueeze(0)
    face = F.interpolate(face, size=(160, 160), mode='bilinear', align_corners=False)
    face = face.to(DEVICE).to(torch.float32) / 255.0
    return face

def get_embedding(input_image):
    face = mtcnn(input_image)
    if face is None:
        return None # Return None if no face detected

    face = preprocess(face)
    with torch.no_grad():
        embedding = resnet(face).cpu().numpy().flatten()
    return embedding


def compare_faces(embedding1, embedding2, threshold=0.6):  # Default threshold is now adjustable
    if embedding1 is None or embedding2 is None:
        return None, False # Handle cases where embeddings are not available

    distance = np.linalg.norm(embedding1 - embedding2)
    return distance, distance < threshold