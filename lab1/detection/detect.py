# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Main script to run the object detection routine."""
import argparse
import sys
import time
import threading
from pathlib import Path
import tempfile
import os

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
#from detection.detect_utils import visualize

class ObjectDetector():

  def __init__(self, objects_of_interest, width: int=640, height: int=480, num_threads: int=4, 
    enable_edgetpu: bool=False):
    """
    Args:
      model: Name of the TFLite object detection model.
      camera_id: The camera id to be passed to OpenCV.
      width: The width of the frame captured from the camera.
      height: The height of the frame captured from the camera.
      num_threads: The number of CPU threads to run the model.
      enable_edgetpu: True/False whether the model is a EdgeTPU model.
    """
    self.model = './efficientdet_lite0.tflite'
    self.camera_id = 0
    self.width = width
    self.height = height
    self.num_threads = num_threads
    self.enable_edgetpu= enable_edgetpu
    self.detect_flag = True
    self.detect_in_pause = False
    #self.detect_t = threading.Thread(target=self.detect, name="ThreadDetect")

    # Visualization parameters
    self.row_size = 20  # pixels
    self.left_margin = 24  # pixels
    self.text_color = (0, 0, 255)  # red
    self.font_size = 1
    self.font_thickness = 1
    self.fps_avg_frame_count = 10

    # To keep track of objects detected
    self.detected = False
    self.objects_of_interest = objects_of_interest
    self.touch_file = '{}/detected.touch'.format(tempfile.gettempdir())

    # Initialize the object detection model
    base_options = core.BaseOptions(
        file_name=self.model, use_coral=self.enable_edgetpu, num_threads=self.num_threads)
    detection_options = processor.DetectionOptions(
        max_results=3, score_threshold=0.3)
    options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options)
    self.detector = vision.ObjectDetector.create_from_options(options)

  def start(self):
      self.detect_t.start()

  def stop(self):
      self.detect_flag = False
      self.detect_t.join()

  def pause(self):
      self.detect_in_pause = True

  def resume(self):
      self.detect_in_pause = False

  def detect(self) -> None:
    """Continuously run inference on images acquired from the camera.

    """

    # Variables to calculate FPS
    counter, fps = 0, 0
    start_time = time.time()


    # Start capturing video input from the camera
    cap = cv2.VideoCapture(self.camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
    cap.set(cv2.CAP_PROP_FPS, 5)

    # Continuously capture images from the camera and run inference
    try:
      while cap.isOpened():
        
        success, image = cap.read()
        if not success:
          sys.exit(
              'ERROR: Unable to read from webcam. Please verify your webcam settings.'
          )

        counter += 1
        image = cv2.flip(image, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(rgb_image)

        # Run object detection estimation using the model.
        detection_result = self.detector.detect(input_tensor)

        # Draw keypoints and edges on input image
        results = visualize(image, detection_result)
        image = results[0]
        objects = results[1]

        found = False
        for o in objects:
         if o[0] in self.objects_of_interest:
           Path(self.touch_file).touch()
           print("found object ", o[0])
           found = True
           break

        if not found:
          if os.path.exists(self.touch_file):
            os.remove(self.touch_file)

        # Calculate the FPS
        if counter % self.fps_avg_frame_count == 0:
          end_time = time.time()
          fps = self.fps_avg_frame_count / (end_time - start_time)
          start_time = time.time()

        # Show the FPS
        fps_text = 'FPS = {:.1f}'.format(fps)
        text_location = (self.left_margin, self.row_size)
        cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    self.font_size, self.text_color, self.font_thickness)

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
          break
        cv2.imshow('object_detector', image)

    finally:
      #self.stop()
      if os.path.exists(self.touch_file):
          os.remove(self.touch_file)
      cap.release()
      print("Camera released.")
      cv2.destroyAllWindows()


if __name__ == '__main__':
  from detect_utils import visualize
  od = ObjectDetector(['stop sign', 'person'])
  #detect('efficientdet_lite0.tflite', 0, 640, 480, 4, False)
  od.detect()
