# pip install opencv-python==3.4.2.16
import sys
import numpy as np
import cv2
from io import open
import socket
import math
import argparse
import time
import multiprocessing

# localhost
UDP_IP = "127.0.0.1"
# komunikacny port
UDP_PORT = 5065
# nacitanie kamery
cap = cv2.VideoCapture(0)
# inicializacia soketu
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
# import vah
faceProto = "C:/Users/livia/Python projekty/agerec/opencv_face_detector.pbtxt"
faceModel = "C:/Users/livia/Python projekty/agerec/opencv_face_detector_uint8.pb"
ageProto = "C:/Users/livia/Python projekty/agerec/age_deploy.prototxt"
ageModel = "C:/Users/livia/Python projekty/agerec/age_net.caffemodel"

# nacitanie siete
ageNet = cv2.dnn.readNet(ageModel, ageProto)
faceNet = cv2.dnn.readNet(faceModel, faceProto)

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
# 8 kategorii datasetu
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']

#padding
padding = 20

#metoda sluziaca ku ziskaniu faceboxov
# vstupom je net, okno a confidence

def getfacebox(net, frame, conf_threshold=0.7):
    #kopirovanie
    frameOpencvDnn = frame.copy()
    # vyska okna
    frameHeight = frameOpencvDnn.shape[0]
    # sirka okna
    frameWidth = frameOpencvDnn.shape[1]
    #parametrami su obraz, scale, velkost, mean,swapRB
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
    #nastavenie vstupu
    net.setInput(blob)
    #ide dopredu k vypoctu net vystupu..vracia pole
    detections = net.forward()
    # uchovava boxy
    rboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        #porovnanie s hranicou
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            #vlozi data do pola
            rboxes.append([x1, y1, x2, y2])
            #vykresli stvorec
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)
    return frameOpencvDnn, rboxes
def framename(name):
    return name
#metoda ktora otvori okno, vypisuje hodnoty a posiela ich do Unity
def predict():
    #pocitadlo pre ukoncenie okna
    counter = 0
    #waitkey caka na event z klavesnice
    while cv2.waitKey(1) < 0:
        #zvysenie pocitadla
        counter+=1
        #time.sleep(setticks(1))
        #tuple kvoli frameOpenCvnDnn
        hasFrame, frame = cap.read()
        #ak nie je frame
        if not hasFrame:
            cv2.waitKey()
            break
        #ziskanie faceboxu
        frameFace, rboxes = getfacebox(faceNet, frame)
        #kontrola ci tvar existuje
        if not rboxes:
            print("Nebola detegovana ziadna tvar")
            continue

        for rbox in rboxes:

            face = frame[max(0, rbox[1] - padding):min(rbox[3] + padding, frame.shape[0] - 1),
                   max(0, rbox[0] - padding):min(rbox[2] + padding, frame.shape[1] - 1)]

            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            #predikcie veku
            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]
            print("Vek : {}, conf = {:.3f}".format(age, agePreds[0].max()))
            #vypis do okna
            cv2.putText(frameFace, age, (rbox[0], rbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2,
                        cv2.LINE_AA)
            #ak sa nachadza v tychto rozmedziach, nemal by mat pristup do hry
            if age == '(0-15)' or age == '(0, 2)' or age == '(4, 6)' or age == '(8, 12)':
                ageRange = 'too young'
                #b1 = bytes(ageRange, encoding='utf-8')
                b1=bytes(age,encoding='utf-8')
                # odosielanie na port
                sock.sendto(b1, (UDP_IP, UDP_PORT))
            # inak moze mat pristup do hry
            else:
                ageRange = 'ok'
                #b1 = bytes(ageRange, encoding='utf-8')
                b1 = bytes(age, encoding='utf-8')
                # odosielanie na port
                sock.sendto(b1, (UDP_IP, UDP_PORT))
            #vytvor okno
            cv2.imshow(framename("detekcia veku"), frameFace)
        #ak je pocitadlo vacsie nez 100 alebo ukoncime input klavesnicou
       # if(counter >setticks(10)) or cv2.waitKey(1) & 0xFF == ord('q'):
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def setticks(ticks):
    return ticks

def main():
    predict()

if __name__ == '__main__':
    # Zaciatok procesu
    p = multiprocessing.Process(target=predict(), name="predict", args=(10,))
    p.start()
    if p.is_alive():
        print("proces bezi, zachvilu bude zabity")
        # Cakaj x sekund
        #time.sleep(setticks(1))
        
        p.terminate()
        print ("proces bol zabity")
        p.join()
    else:
        print("proces nezacal")
