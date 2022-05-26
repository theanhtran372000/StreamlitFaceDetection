import cv2
import sys
import os
import numpy as np

sys.path.append(os.path.join('insightface', 'recognition', 'arcface_mxnet','common'))
import face_align

class FaceDetection():
    def __init__(self, video_capture):
        self.face_detector = cv2.FaceDetectorYN.create('model/yunet.onnx', "", (0, 0))
        self.video_capture = video_capture
        
        width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.input_size = (width, height)
        self.face_detector.setInputSize((width, height))
    
    def detect(self, image):
        # Detect face
        _, faces = self.face_detector.detect(image)
        
        if faces is None:
            return None, None
        
        else:
            cropped_faces = []
            loc_faces = []
            
            for face in list(faces):
                lm, loc = self.analyze_face(face)
                
                if loc[2] * loc[3] < 30 * 30:
                    continue
                
                cropped_face = self.get_norm_crop(image, lm)
                
                cropped_faces.append(cropped_face)
                loc_faces.append(loc)
                
            return cropped_faces, loc_faces
                
    def analyze_face(self, face):
        conf = face[-1]
        loc = list(map(int, face[:4]))
        lm = np.reshape(face[4:-1], (5, 2))
        return lm, loc
    
    def get_norm_crop(self, image, landmark):
        return face_align.norm_crop(
            image,
            landmark=landmark,
            image_size=112,
            mode='arc_face'
        )