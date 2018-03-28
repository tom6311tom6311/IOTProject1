#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import re
import shutil
import numpy as np
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult, IoTHubError
from scipy.misc import *

# App constants
CONNECTION_STRING = 'HostName=tom6311tom6311-demo.azure-devices.net;DeviceId=rpi-hardware-test;SharedAccessKey=Ta0czoj3OpsoGlzTbPy68vCvsFqmHCQDJnGK5P5se2I='
CONNECTION_PROTOCOL = IoTHubTransportProvider.HTTP
EVENT_SUCCESS = "success"
EVENT_FAILED = "failed"
SOUND_SENSOR_CHANNEL = 12
IMAGE_FORMAT = '.png'
PHOTO_FOLDER = 'photos/'
REGULAR_SHOT_INTERVAL = 60
COSINE_SIMILARITY_THRESHOLD = .8

def sigmoid(x):
  return 1 / (1 + np.exp(-x))

def iothub_client_init():
  client = IoTHubClient(CONNECTION_STRING, CONNECTION_PROTOCOL)
  return client

def take_photo(file_name):
  os.system("raspistill -o " + PHOTO_FOLDER + file_name)

def upload_photo(file_name):
  f = open(PHOTO_FOLDER + file_name, "r")
  content = f.read()
  client.upload_blob_async(file_name, content, len(content), photo_upload_callback, 0)
  print ( "" )
  print ( "Uploading photo..." )

def compute_diff_photo(file_name, prev_file_name):
  abnormal_img = imread(PHOTO_FOLDER + file_name)
  normal_img = imread(PHOTO_FOLDER + prev_file_name)
  abnormal_pt_norm = np.sqrt(np.sum(np.square(abnormal_img), axis=2))
  normal_pt_norm = np.sqrt(np.sum(np.square(normal_img), axis=2))
  dot = np.sum(abnormal_img * normal_img, axis=2)
  cosine_sim = dot / (abnormal_pt_norm * normal_pt_norm)
  cosine_sim = np.transpose(np.array([cosine_sim, cosine_sim, cosine_sim]), axes=[1,2,0])
  diff_img_mask = (cosine_sim < COSINE_SIMILARITY_THRESHOLD).astype(int)
  diff_img = np.multiply(diff_img_mask, abnormal_img).astype(int)
  diff_photo_name = 'diff_' + file_name
  imsave(PHOTO_FOLDER + diff_photo_name, diff_img)
  return diff_photo_name

def abnormal_sound_callback(channel):
  if GPIO.input(channel)== GPIO.LOW:
    # print("Sound low!")
    pass
  else:
    curr_time = time.strftime("%Y.%m.%d-%H.%M.%S")
    photo_name = curr_time + '_abnormal' + IMAGE_FORMAT
    print("A loud sound occurred at " + curr_time)
    take_photo(photo_name)
    diff_photo_name = compute_diff_photo(photo_name, prev_regular_photo_name)
    upload_photo(diff_photo_name)

def photo_upload_callback(result, user_context):
  if str(result) == 'OK':
    print ( "Uploaded" )
  else:
    print ( "Error: " + str(result) )

def parse_iot_hub_name():
  m = re.search("HostName=(.*?)\.", CONNECTION_STRING)
  return m.group(1)


if __name__ == "__main__":
  # create photo folder
  if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

  #GPIO SETUPs
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(SOUND_SENSOR_CHANNEL, GPIO.IN)

  try:
    client = iothub_client_init()
    GPIO.add_event_detect(SOUND_SENSOR_CHANNEL, GPIO.BOTH, bouncetime=300)
    GPIO.add_event_callback(SOUND_SENSOR_CHANNEL, abnormal_sound_callback)
    start_time = int(time.time())
    while True:
      if (int(time.time()) - start_time) % REGULAR_SHOT_INTERVAL == 0:
        curr_time = time.strftime("%Y.%m.%d-%H.%M.%S")
        print("Take a regular shot: " + curr_time)
        prev_regular_photo_name = curr_time + IMAGE_FORMAT
        take_photo(prev_regular_photo_name)
      time.sleep(1)
  except IoTHubError as iothub_error:
    print ( "Unexpected error %s from IoTHub" % iothub_error )
  except KeyboardInterrupt:
    print ( "IoTHubClient stopped" )
