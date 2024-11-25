import gpiozero
import time
import sys
import os
import cv2
import threading
import base64
import pytz

from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore

from paho.mqtt import client as mqtt_client
from gpiozero import OutputDevice as stepper

cred = credentials.Certificate("./google-services.json")
firebase_url = "https://976168498897.firebaseio.com/"
firebase_admin.initialize_app(cred)
db = firestore.client()
cam_photos_ref = db.collection('cam_photos')

broker = 'broker.emqx.io'
port = 1883
topic = '/puc/eng/patacheia'
one = 0

IN1 = stepper(12)
IN2 = stepper(16)
IN3 = stepper(20)
IN4 = stepper(21)

stepPins = [IN1, IN2, IN3, IN4]
stepDir = -1
seq = [[1, 0, 0, 1], 
       [1, 0, 0, 0], 
       [1, 1, 0, 0], 
       [0, 1, 0, 0], 
       [0, 1, 1, 0], 
       [0, 0, 1, 0], 
       [0, 0, 1, 1], 
       [0, 0, 0, 1]]

MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
RECONNECT_RATE = 2
FIRST_RECONNECT_DELAY = 1

led = gpiozero.LED(19)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connect to MQTT Broker")
        else:
            print("Failed. Error: %d\n", rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_disconnect(client, userdata, rc):
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        try:
            client.reconnect()
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def subscribe(client: mqtt_client):
    global one
    def on_message(client, userdata, msg):
        global one
        print(msg.payload.decode())
        one = one + 1
        if msg.payload.decode() == 'open' and one != 0:
            start_motor()

    client.subscribe(topic)
    client.on_message = on_message

def start_motor():
    stepCount = len(seq)
    waitTime = int(sys.argv[1])/float(1000) if len(sys.argv) > 1 else 0.003
    stepCounter = 0
    while True:
        for pin in range(0, 4):
            xPin = stepPins[pin]
            if seq[stepCounter][pin] != 0:
                xPin.on()
            else:
                xPin.off()
        stepCounter += stepDir
        if stepCounter >= stepCount:
            stepCounter = 0
        if stepCounter < 0:
            stepCounter = stepCount + stepDir
        time.sleep(waitTime)

def save_photo(frame, path="fotos", prefix="animal_detectado"):
    if not os.path.exists(path):
        os.makedirs(path)

    date = datetime.now()
    new_date = date - timedelta(hours=3)
    new_date = new_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    file_save = os.path.join(path, f"{prefix}_{new_date}.jpg")
    cv2.imwrite(file_save, frame)
    base64_data = convert_base64(file_save)

    new_document = cam_photos_ref.add({
        'base64': 'data:image/jpeg;base64,' + base64_data,
        'petId': '',
        'time': new_date
    })
    print(f"Photo saved: {file_save}")

def activate_camera():
    prototxt = "MobileNetSSD_deploy.prototxt"
    model = "MobileNetSSD_deploy.caffemodel"
    net = cv2.dnn.readNetFromCaffe(prototxt, model)

    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", 
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", 
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep", 
               "sofa", "train", "tvmonitor"]

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error accessing the camera.")
        return

    print("Camera activated. Press 'q' to exit.")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error capturing the frame.")
            break

        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                idx = int(detections[0, 0, i, 1])
                if CLASSES[idx] in ["dog", "cat"]:
                    box = detections[0, 0, i, 3:7] * [w, h, w, h]
                    (start_x, start_y, end_x, end_y) = box.astype("int")
                    label = f"{CLASSES[idx]}: {confidence:.2f}"
                    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
                    cv2.putText(frame, label, (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    save_photo(frame)
                    time.sleep(2)

        cv2.imshow("Animal Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

def convert_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def mqtt_loop():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

def run():
    thread1 = threading.Thread(target=mqtt_loop)
    thread2 = threading.Thread(target=activate_camera)

    thread1.start()
    thread2.start()

if __name__ == '__main__':
    run()
