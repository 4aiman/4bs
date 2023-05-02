# load_save_image.py

import cv2
import sys
import numpy
import sounddevice as sd
from pygrabber.dshow_graph import FilterGraph
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import qimage2ndarray
import time
import math


graph = FilterGraph()

video_devices = graph.get_input_devices()
selected_video_device = cv2.VideoCapture(video_devices.index(video_devices[0]))

sound_devices = sd.query_devices()
selected_sound_device = sound_devices[0]
selected_output_sound_device = sound_devices[0]


def on_sound_output_combobox_changed(index):
    global selected_output_sound_device
    selected_output_sound_device = sound_devices[index-1]
    print("selected output audio device:", selected_output_sound_device['name'])

def on_sound_combobox_changed(index):
    global selected_sound_device
    selected_sound_device = sound_devices[index-1]
    print("selected audio device:", selected_sound_device['name'])
    # do your code

def on_video_combobox_changed(index):
    try:
        global selected_video_device
        selected_video_device = cv2.VideoCapture(video_devices.index(video_devices[index-1]))
        selected_video_device.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
        selected_video_device.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
        fps = int(selected_video_device.get(5))
        print("fps:", fps)
        print("selected video device:", video_devices[index-1])
    except:
        print("f")

def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata


def display_video_stream():
        """Read frame from camera and repaint QLabel widget.
        """
        now = time.time()
        global gtime
        global counter

        
        fps = math.ceil(1/(now-gtime))
        
        ret, frame = selected_video_device.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame = cv2.flip(frame, 1)
        image = qimage2ndarray.array2qimage(frame)  #SOLUTION FOR MEMORY LEAK
        label.setPixmap(QPixmap.fromImage(image))        
        counter = counter + 1        
        
        if fps <60:
            caption = "frames:" + str(counter)+ " <font color='red'>fps:"+ str(fps)+'</font>'
        else:
            caption = "frames:" + str(counter)+ " fps:"+ str(fps)
        fps_label.setText(caption)
        #print(caption)
        gtime = now
        
        

counter = 0
gtime = time.time()

# 1. Import QApplication and all the required widgets
app = QApplication([sys.argv])
window = QWidget()
window.setWindowTitle("PyQt: 4BS (For the great BS!)")
window.setGeometry(100, 100, 1600, 900)

fps_label = QLabel("", parent=window)
fps_label.move(15, 850)
fps_label.resize(1280, 30)

label = QLabel("image", parent=window)
label.move(15, 110)
label.resize(1280, 720)

# device list
sound_output_devicelist_label = QLabel("Output sound device:", parent=window)
sound_output_devicelist_label.move(15, 15)
sound_output_devicelist_combo = QComboBox(parent=window)
sound_output_devicelist_combo.move(140, 12)
sound_output_devicelist_combo.resize(200, 24)

sound_devicelist_label = QLabel("Sound device:", parent=window)
sound_devicelist_label.move(15, 45)
sound_devicelist_combo = QComboBox(parent=window)
sound_devicelist_combo.move(140, 42)
sound_devicelist_combo.resize(200, 24)

video_devicelist_label = QLabel("Video device:", parent=window)
video_devicelist_label.move(15, 75)
video_devicelist_combo = QComboBox(parent=window)
video_devicelist_combo.move(140, 72)
video_devicelist_combo.resize(200, 24)

for device in sound_devices:
    sound_output_devicelist_combo.addItem(device['name'], device)
    sound_devicelist_combo.addItem(device['name'], device)
    

for device in video_devices:
    video_devicelist_combo.addItem(device)

sound_output_devicelist_combo.currentIndexChanged.connect(on_sound_output_combobox_changed)
sound_devicelist_combo.currentIndexChanged.connect(on_sound_combobox_changed)
video_devicelist_combo.currentIndexChanged.connect(on_video_combobox_changed)


video_devicelist_combo.setCurrentIndex(3)
sound_devicelist_combo.setCurrentIndex(2)
sound_output_devicelist_combo.setCurrentIndex(6)


timer = QTimer()
timer.timeout.connect(display_video_stream)
timer.start(15)


sd.Stream(device=(sound_devicelist_combo.currentIndex(), sound_output_devicelist_combo.currentIndex()), channels=2, callback=callback).start()
    

window.show()
app.exec()
