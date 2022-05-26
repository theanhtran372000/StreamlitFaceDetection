import os
import cv2
import time
from cv2 import VideoCapture
import streamlit as st
from face_detection import FaceDetection

# Side bar
st.sidebar.header('Control Panel')

# Config
st.sidebar.subheader('Config')
st.sidebar.slider('Detection threshold', min_value=0.0, max_value=1.0, value=0.5)
app_mode = st.sidebar.select_slider('Mode', ['Checkin mode', 'Registation Mode'], 'Checkin mode')

# System stats
st.sidebar.subheader('Stats')
stats = st.sidebar.markdown('Stats')

# Control
st.sidebar.subheader('Control')
exit_button = st.sidebar.button('Exit')

# Main bar
st.subheader('Real-time Face Detection')
display = st.image([])

def main():
    if app_mode == 'Checkin mode':
        
        # Video capture device
        video_capture = cv2.VideoCapture(0)
        
        # Face Detection model
        model = FaceDetection(video_capture)
        
        print('Starting at resolution: {}x{}'.format(model.input_size[1], model.input_size[0]))  
        
        
        while not exit_button:
            begin = time.time()
            
            suc, frame = video_capture.read()
            
            if suc:
                faces, locs = model.detect(frame)
                
                # Draw recs
                if faces is not None:
                    for loc in locs:
                        cv2.rectangle(frame, loc, (244, 134, 66), cv2.LINE_4)
                
                # Display image
                display.image(frame, channels='BGR', use_column_width=True)
                del frame
                
                # Display stats
                total = time.time() - begin
                
                stats.write('''
                        * FPS - {:>8.1f}FPS

                        * Time - {:>8.3f}s

                        * Faces - {:>8}
                            '''.format(
                                1/total,
                                total,
                                len(faces) if faces is not None else 0
                            ))
            else:
                print('Cant capture image!')
            

if __name__ == '__main__':
    main()
