"""
CYBERABAD TRAFFIC NEXUS - OpenCV Computer Vision Module
Processes traffic camera feeds and performs vehicle/face detection
"""

import cv2
import numpy as np
from datetime import datetime
import random
import os

class TrafficCameraProcessor:
    """Process traffic camera feeds with computer vision"""
    
    def __init__(self):
        self.vehicle_cascade = None
        self.face_cascade = None
        self.load_cascades()
    
    def load_cascades(self):
        """Load Haar cascades for detection"""
        try:
            # Try to load OpenCV's built-in cascades
            cascade_path = cv2.data.haarcascades
            self.vehicle_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_car.xml'
            )
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        except Exception as e:
            print(f"Cascade loading error: {e}")
    
    def detect_vehicles(self, frame):
        """Detect vehicles in frame using motion detection"""
        if frame is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # For simulation, return random detections
        vehicles = []
        num_vehicles = random.randint(3, 12)
        
        height, width = frame.shape[:2]
        
        for _ in range(num_vehicles):
            x = random.randint(50, width - 100)
            y = random.randint(int(height * 0.3), int(height * 0.7))
            w = random.randint(40, 80)
            h = random.randint(30, 60)
            
            vehicles.append({
                'bbox': (x, y, w, h),
                'type': random.choice(['car', 'truck', 'bus', 'bike']),
                'confidence': random.uniform(0.7, 0.95)
            })
        
        return vehicles
    
    def detect_faces(self, frame):
        """Detect faces in frame"""
        if frame is None:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return len(faces)
    
    def count_vehicles(self, frame):
        """Count vehicles in frame"""
        vehicles = self.detect_vehicles(frame)
        return len(vehicles)
    
    def analyze_traffic_density(self, frame):
        """Analyze traffic density"""
        if frame is None:
            return {'density': 0, 'status': 'unknown'}
        
        vehicles = self.detect_vehicles(frame)
        count = len(vehicles)
        
        if count < 5:
            density = "low"
            congestion = 0.2
        elif count < 10:
            density = "medium"
            congestion = 0.5
        elif count < 15:
            density = "high"
            congestion = 0.75
        else:
            density = "critical"
            congestion = 0.95
        
        return {
            'density': density,
            'count': count,
            'congestion_score': congestion,
            'status': 'congested' if congestion > 0.6 else 'flowing'
        }
    
    def detect_violations(self, frame):
        """Detect traffic violations"""
        violations = {
            'helmet': 0,
            'mobile': 0,
            'signal_jump': 0,
            'over_speed': 0
        }
        
        # Simulate violation detection
        violations['helmet'] = random.randint(0, 3)
        violations['mobile'] = random.randint(0, 2)
        
        return violations
    
    def process_frame(self, frame):
        """Process single frame and return analysis"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'vehicle_count': 0,
            'face_count': 0,
            'traffic_density': 'low',
            'violations': {},
            'speed_estimate': 0,
            'flow_direction': 'both'
        }
        
        if frame is not None:
            analysis['vehicle_count'] = self.count_vehicles(frame)
            analysis['face_count'] = self.detect_faces(frame)
            
            density_result = self.analyze_traffic_density(frame)
            analysis['traffic_density'] = density_result['density']
            analysis['congestion_score'] = density_result['congestion_score']
            
            analysis['violations'] = self.detect_violations(frame)
            
            # Estimate average speed based on density
            if analysis['traffic_density'] == 'low':
                analysis['speed_estimate'] = random.uniform(40, 60)
            elif analysis['traffic_density'] == 'medium':
                analysis['speed_estimate'] = random.uniform(25, 40)
            elif analysis['traffic_density'] == 'high':
                analysis['speed_estimate'] = random.uniform(10, 25)
            else:
                analysis['speed_estimate'] = random.uniform(5, 15)
        
        return analysis
    
    def create_simulation_frame(self, width=640, height=360, density="medium"):
        """Create a simulated traffic camera frame"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Sky gradient
        for i in range(height // 2):
            frame[i, :] = [max(20, 50 - i // 2), max(30, 60 - i // 2), max(40, 80 - i // 2)]
        
        # Ground
        frame[height // 2:, :] = [40, 40, 40]
        
        # Road
        road_top = int(height * 0.4)
        road_bottom = int(height * 0.6)
        frame[road_top:road_bottom, :] = [50, 50, 50]
        
        # Road markings
        for x in range(0, width, 40):
            cv2.line(frame, (x, height // 2), (x + 20, height // 2), (255, 255, 255), 2)
        
        # Add vehicles based on density
        num_vehicles = {"low": 3, "medium": 7, "high": 12, "critical": 18}.get(density, 7)
        
        for _ in range(num_vehicles):
            x = random.randint(0, width - 60)
            y = random.randint(road_top + 10, road_bottom - 30)
            
            color = (
                random.randint(150, 255),
                random.randint(150, 255),
                random.randint(150, 255)
            )
            
            # Draw vehicle
            cv2.rectangle(frame, (x, y), (x + 50, y + 25), color, -1)
            cv2.rectangle(frame, (x + 5, y - 10), (x + 20, y), color, -1)  # Windshield
        
        # Add text overlay
        cv2.putText(frame, f"CAM-01 | {density.upper()} TRAFFIC", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame


class FaceRecognitionProcessor:
    """Process face detection and recognition"""
    
    def __init__(self):
        self.known_faces = []
        self.tolerance = 0.6
    
    def encode_face(self, face_image):
        """Encode a face for storage"""
        # Simple encoding - in production use dlib or face_recognition library
        if face_image is not None:
            return hash(face_image.tobytes())
        return None
    
    def compare_faces(self, encoding1, encoding2):
        """Compare two face encodings"""
        if encoding1 is None or encoding2 is None:
            return False
        return abs(encoding1 - encoding2) < self.tolerance
    
    def detect_and_recognize(self, frame):
        """Detect and recognize faces"""
        processor = TrafficCameraProcessor()
        num_faces = processor.detect_faces(frame)
        
        return {
            'face_count': num_faces,
            'recognized': [],
            'unknown': max(0, num_faces - len(self.known_faces))
        }


# Simulated camera feed generator
def generate_camera_feed(camera_id, width=640, height=360):
    """Generate simulated camera feed data"""
    processor = TrafficCameraProcessor()
    
    densities = ["low", "medium", "high", "critical"]
    weights = [0.2, 0.4, 0.3, 0.1]
    density = random.choices(densities, weights=weights)[0]
    
    frame = processor.create_simulation_frame(width, height, density)
    analysis = processor.process_frame(frame)
    
    return {
        'camera_id': camera_id,
        'frame': frame,
        'analysis': analysis,
        'timestamp': datetime.now().isoformat()
    }


# Export for use in other modules
__all__ = ['TrafficCameraProcessor', 'FaceRecognitionProcessor', 'generate_camera_feed']
