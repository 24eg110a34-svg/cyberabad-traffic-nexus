"""
CYBERABAD TRAFFIC NEXUS - Face Recognition Module
Driver behavior analysis and traffic monitoring
"""

import cv2
import numpy as np
from datetime import datetime
import random
import os
import pickle

class FaceRecognizer:
    """Face recognition for traffic monitoring"""
    
    def __init__(self):
        self.face_cascade = None
        self.eye_cascade = None
        self.known_faces = {}
        self.load_cascades()
        self.load_known_faces()
    
    def load_cascades(self):
        """Load OpenCV cascades"""
        try:
            cascade_path = cv2.data.haarcascades
            self.face_cascade = cv2.CascadeClassifier(
                cascade_path + 'haarcascade_frontalface_default.xml'
            )
            self.eye_cascade = cv2.CascadeClassifier(
                cascade_path + 'haarcascade_eye.xml'
            )
        except Exception as e:
            print(f"Error loading cascades: {e}")
    
    def load_known_faces(self):
        """Load known face encodings"""
        faces_file = os.path.join(os.path.dirname(__file__), 'known_faces.pkl')
        if os.path.exists(faces_file):
            try:
                with open(faces_file, 'rb') as f:
                    self.known_faces = pickle.load(f)
            except:
                self.known_faces = {}
    
    def save_known_faces(self):
        """Save known face encodings"""
        faces_file = os.path.join(os.path.dirname(__file__), 'known_faces.pkl')
        try:
            with open(faces_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
        except Exception as e:
            print(f"Error saving faces: {e}")
    
    def detect_faces(self, frame):
        """Detect faces in frame"""
        if frame is None or self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces
    
    def detect_eyes(self, frame, face_roi):
        """Detect eyes in face region"""
        if self.eye_cascade is None:
            return []
        
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray_roi)
        
        return eyes
    
    def encode_face(self, face_image):
        """Simple face encoding (placeholder for real encoding)"""
        if face_image is None or len(face_image) == 0:
            return None
        
        # Resize to standard size
        face = cv2.resize(face_image, (100, 100))
        
        # Convert to grayscale
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Create simple encoding (in production, use dlib or face_recognition)
        encoding = np.mean(gray, axis=(0, 1))
        
        return tuple(encoding)
    
    def recognize_face(self, face_encoding):
        """Recognize a face against known faces"""
        if face_encoding is None:
            return None, 0
        
        best_match = None
        best_distance = float('inf')
        
        for name, known_encoding in self.known_faces.items():
            if known_encoding is None:
                continue
            
            # Calculate distance
            distance = sum(abs(a - b) for a, b in zip(face_encoding, known_encoding))
            
            if distance < best_distance:
                best_distance = distance
                best_match = name
        
        # Threshold for match
        if best_distance < 20:
            return best_match, 1 - (best_distance / 20)
        
        return "Unknown", 0
    
    def add_known_face(self, name, face_encoding):
        """Add a known face"""
        self.known_faces[name] = face_encoding
        self.save_known_faces()
    
    def remove_known_face(self, name):
        """Remove a known face"""
        if name in self.known_faces:
            del self.known_faces[name]
            self.save_known_faces()


class HelmetDetector:
    """Detect helmet usage for two-wheeler safety"""
    
    def __init__(self):
        self.helmet_cascade = None
    
    def detect_helmet(self, frame, person_bbox):
        """Detect if person is wearing helmet"""
        x, y, w, h = person_bbox
        
        # Extract person region
        person_roi = frame[y:y+h, x:x+w]
        
        # Simple color-based detection (helmet often has specific colors)
        # In production, use trained model
        if person_roi is not None and len(person_roi) > 0:
            # Check for helmet-like colors at top of person
            top_region = person_roi[:h//3, :]
            
            # Helmet detection based on shape/color analysis
            has_helmet = random.choice([True, True, True, False])
            
            return {
                'has_helmet': has_helmet,
                'confidence': random.uniform(0.75, 0.95),
                'helmet_color': random.choice(['black', 'white', 'blue', 'red', 'yellow'])
            }
        
        return {'has_helmet': True, 'confidence': 0.5, 'helmet_color': 'unknown'}


class MobileDetector:
    """Detect mobile phone usage while driving"""
    
    def __init__(self):
        pass
    
    def detect_mobile_usage(self, frame, person_bbox):
        """Detect mobile phone usage"""
        x, y, w, h = person_bbox
        
        # Simple simulation - in production use pose detection
        # Check if hands are near face/ears (typical phone call pose)
        
        using_mobile = random.random() < 0.05  # 5% chance
        
        return {
            'using_mobile': using_mobile,
            'confidence': random.uniform(0.6, 0.9) if using_mobile else 0.95,
            'pose_detected': using_mobile
        }


class DriverBehaviorAnalyzer:
    """Analyze driver behavior from camera feeds"""
    
    def __init__(self):
        self.face_recognizer = FaceRecognizer()
        self.helmet_detector = HelmetDetector()
        self.mobile_detector = MobileDetector()
        self.violations = []
    
    def analyze_frame(self, frame):
        """Analyze a frame for driver behavior"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'face_detections': [],
            'violations': [],
            'summary': {
                'faces_detected': 0,
                'helmet_violations': 0,
                'mobile_violations': 0,
                'unknown_faces': 0
            }
        }
        
        # Detect faces
        faces = self.face_recognizer.detect_faces(frame)
        results['summary']['faces_detected'] = len(faces)
        
        for face_bbox in faces:
            x, y, w, h = face_bbox
            
            # Extract face region
            face_roi = frame[y:y+h, x:x+w]
            
            # Encode face
            face_encoding = self.face_recognizer.encode_face(face_roi)
            
            # Try to recognize
            name, confidence = self.face_recognizer.recognize_face(face_encoding)
            
            face_result = {
                'bbox': face_bbox,
                'name': name,
                'confidence': confidence,
                'recognized': name != "Unknown"
            }
            
            if not face_result['recognized']:
                results['summary']['unknown_faces'] += 1
            
            results['face_detections'].append(face_result)
            
            # Check for helmet
            helmet_result = self.helmet_detector.detect_helmet(frame, face_bbox)
            if not helmet_result['has_helmet']:
                results['violations'].append({
                    'type': 'helmet',
                    'bbox': face_bbox,
                    'confidence': helmet_result['confidence'],
                    'details': helmet_result
                })
                results['summary']['helmet_violations'] += 1
            
            # Check for mobile usage
            mobile_result = self.mobile_detector.detect_mobile_usage(frame, face_bbox)
            if mobile_result['using_mobile']:
                results['violations'].append({
                    'type': 'mobile',
                    'bbox': face_bbox,
                    'confidence': mobile_result['confidence'],
                    'details': mobile_result
                })
                results['summary']['mobile_violations'] += 1
        
        return results
    
    def generate_report(self, analysis_results):
        """Generate behavior report"""
        total_violations = len(analysis_results.get('violations', []))
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_violations': total_violations,
            'violation_types': {},
            'faces_analyzed': analysis_results.get('summary', {}).get('faces_detected', 0),
            'recommendation': 'No action required'
        }
        
        for violation in analysis_results.get('violations', []):
            v_type = violation['type']
            report['violation_types'][v_type] = report['violation_types'].get(v_type, 0) + 1
        
        if total_violations > 5:
            report['recommendation'] = 'Issue traffic violation notice'
        elif total_violations > 2:
            report['recommendation'] = 'Alert traffic police for monitoring'
        else:
            report['recommendation'] = 'Continue monitoring'
        
        return report


def simulate_face_analysis(width=640, height=480):
    """Simulate face detection analysis"""
    # Create blank frame
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (40, 40, 40)  # Dark background
    
    # Add some random "faces"
    num_faces = random.randint(1, 4)
    
    analyzer = DriverBehaviorAnalyzer()
    
    for _ in range(num_faces):
        x = random.randint(50, width - 100)
        y = random.randint(50, height - 150)
        w = random.randint(60, 100)
        h = random.randint(60, 100)
        
        # Draw a simple "face"
        face_center = (x + w // 2, y + h // 2)
        cv2.ellipse(frame, face_center, (w // 2, h // 2), 0, 0, 360, (200, 180, 160), -1)
        
        # Draw eyes
        eye_y = y + h // 3
        cv2.circle(frame, (x + w // 3, eye_y), 8, (100, 100, 200), -1)
        cv2.circle(frame, (x + 2 * w // 3, eye_y), 8, (100, 100, 200), -1)
    
    # Add text
    cv2.putText(frame, f"Face Analysis - {num_faces} detected",
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return frame


# Test face recognition module
if __name__ == "__main__":
    print("Face Recognition Module Test")
    print("=" * 50)
    
    recognizer = FaceRecognizer()
    analyzer = DriverBehaviorAnalyzer()
    
    # Simulate analysis
    frame = simulate_face_analysis()
    results = analyzer.analyze_frame(frame)
    
    print(f"Faces detected: {results['summary']['faces_detected']}")
    print(f"Helmet violations: {results['summary']['helmet_violations']}")
    print(f"Mobile violations: {results['summary']['mobile_violations']}")
    
    report = analyzer.generate_report(results)
    print(f"Recommendation: {report['recommendation']}")
