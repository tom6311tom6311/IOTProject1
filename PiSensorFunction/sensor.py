#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import datetime
import os
import re
import shutil
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult, IoTHubError

# App constants
CONNECTION_STRING = 'HostName=tom6311tom6311-demo.azure-devices.net;DeviceId=rpi-hardware-test;SharedAccessKey=Ta0czoj3OpsoGlzTbPy68vCvsFqmHCQDJnGK5P5se2I='
CONNECTION_PROTOCOL = IoTHubTransportProvider.HTTP
EVENT_SUCCESS = "success"
EVENT_FAILED = "failed"
SOUND_SENSOR_CHANNEL = 12
PHOTO_DELAY = 3
IMAGE_FORMAT = '.png'
PHOTO_FOLDER = 'photos/'

def iothub_client_init():
  client = IoTHubClient(CONNECTION_STRING, CONNECTION_PROTOCOL)
  return client

def take_photo(file_name):
  os.system("raspistill -o " + PHOTO_FOLDER + file_name)
  time.sleep(PHOTO_DELAY)

def upload_photo(file_name):
  f = open(PHOTO_FOLDER + file_name, "r")
  content = f.read()
  client.upload_blob_async(file_name, content, len(content), photo_upload_callback, 0)
  print ( "" )
  print ( "Uploading photo..." )

def abnormal_sound_callback(channel):
  if GPIO.input(channel)== GPIO.LOW:
    # print("Sound low!")
    pass
  else:
    curr_time = time.strftime("%Y.%m.%d-%H.%M.%S")
    photo_name = curr_time + IMAGE_FORMAT
    print("A loud sound occurred at " + curr_time)
    take_photo(photo_name)
    upload_photo(photo_name)

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
    while True:
      time.sleep(1)
  except IoTHubError as iothub_error:
    print ( "Unexpected error %s from IoTHub" % iothub_error )
  except KeyboardInterrupt:
    print ( "IoTHubClient stopped" )
