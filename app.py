import os
import cv2
import time
from matplotlib.pyplot import draw
import psutil
import streamlit as st
from face_detection import FaceDetection
from benchmark import Tracker, GraphDrawer

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

# Config Tracker
save_dir = './benchmark/saved'
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
    
tracker = Tracker(save_dir)
tracker.add_criteria(['t_total', 't_capture', 't_detect', 't_drawrec', 't_display', 'fps', 'cpu', 'ram'])
tracker.config_scheduler(every=30, period='second')

def main():
    if app_mode == 'Checkin mode':
        # Display in Checkin mode
        # Main bar
        st.subheader('Real-time Face Detection')
        display = st.image([])
        
        st.markdown('---')
        
        # Graph
        st.subheader('Graph')
        
        # Draw graph
        drawer = GraphDrawer(tracker)
        drawer.add_graph('time', ['time', 't_total', 't_capture', 't_detect', 't_drawrec', 't_display'], index='time')
        drawer.add_graph('fps', ['time', 'fps'], index='time')
        drawer.add_graph('cpu', ['time', 'cpu'], index='time')
        drawer.add_graph('ram', ['time', 'ram'], index='time')
        drawer.config_scheduler(every=30, period='second')
        
        # Video capture device
        video_capture = cv2.VideoCapture(0)
        
        # Face Detection model
        model = FaceDetection(video_capture)
        
        print('Starting at resolution: {}x{}'.format(model.input_size[1], model.input_size[0]))  
        
        since = time.time()
        UPDATE_EVERY = 30 # second
        
        # Config Tracker
        while not exit_button:
            begin = time.time()
            suc, frame = video_capture.read()
            t_capture = time.time() - begin
            
            if suc:
                begin = time.time()
                faces, locs = model.detect(frame)
                t_detect = time.time() - begin
                
                # Draw recs
                begin = time.time()
                if faces is not None:
                    for loc in locs:
                        cv2.rectangle(frame, loc, (244, 134, 66), cv2.LINE_4)
                t_drawrec = time.time() - begin
                
                # Display image
                begin = time.time()
                display.image(frame, channels='BGR', use_column_width=True)
                del frame
                t_display = time.time() - begin
                
                # Display stats
                t_total = t_capture + t_detect + t_drawrec + t_display
                
                stats.write('''
                        * FPS - {:>8.1f}FPS

                        * Time - {:>8.3f}s

                        * Faces - {:>8}
                            '''.format(
                                1/t_total,
                                t_total,
                                len(faces) if faces is not None else 0
                            ))
                
                tracker.track({
                    't_total': t_total,
                    't_capture': t_capture, 
                    't_detect': t_detect, 
                    't_drawrec': t_drawrec, 
                    't_display': t_display, 
                    'fps': 1/t_total, 
                    'cpu': psutil.cpu_percent(), 
                    'ram': psutil.virtual_memory().percent
                })
                
                # Check update graphs
                drawer.run_pending()
                
            else:
                print('Cant capture image!')
            

if __name__ == '__main__':
    main()
