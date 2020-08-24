import cv2
from pyzbar.pyzbar import decode
import socket
import time
import os
import script
import numpy as np
from openvino.inference_engine import IECore


def DecideParams():
    try:
        if os.uname()[4][:3] == 'arm':
            print('RPi found')
            Platform='RPiOS'
        else:
            print('CPU found, unix')
            Platform = 'UNIX'
    except:
        Platform = 'WIN'

    return Platform

def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

Platform = DecideParams()
testmod = False
Video = True

if Platform=='RPiOS' or Platform=='UNIX' or testmod:

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("programm", cv2.WND_PROP_FULLSCREEN)          
    cv2.setWindowProperty("programm", cv2.WND_PROP_FULLSCREEN, 1)

    if cap is None or not cap.isOpened():
        blank_image = np.zeros((480,640,3), np.uint8)
        cv2.putText(blank_image,'No Camera found', (320,240),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
        while cap is None or not cap.isOpened():
            cv2.imshow("programm", blank_image)
            cv2.waitKey(50)
            cap = cv2.VideoCapture(0)
    print('camera found')
    
    ie = IECore()
    Device_List = ie.available_devices
    while len(Device_List)==0:
        blank_image = np.zeros((480,640,3), np.uint8)
        cv2.putText(blank_image,'No OpenVinoDevice', (320,240),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
        cv2.imshow("programm", blank_image)
        cv2.waitKey(50)
        time.sleep(5)
        Device_List = ie.available_devices
    print('OpenVinoDevice found')

    isconnect=False
    if not testmod:
        time_start = time.time()
        isconnect = is_connected()
        try_to_connect = not isconnect
        while try_to_connect:
            time.sleep(5)
            blank_image = np.zeros((480,640,3), np.uint8)
            cv2.putText(blank_image,'TryConnectToInternet', (320,240),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
            cv2.imshow("programm", blank_image)
            cv2.waitKey(50)
            if time.time()-time_start<30:
                try_to_connect=True

            else:
                try_to_connect=False

                fw = open('log2.txt', 'a')
                fw.write('connected on start' +'\n')
                fw.close()
            if is_connected():
                try_to_connect=False
                fw = open('log2.txt', 'a')
                fw.write('already connected on start' +'\n')
                fw.close()
        fw = open('log2.txt', 'a')
        fw.write(str(time.time()-time_start) +'\n')
        fw.close()

    if not is_connected():
        if Platform=='RPiOS' or Platform=='UNIX':
            if os.path.isfile("wpa_supplicant_auto.conf"):  
                script.reconnect("wpa_supplicant_auto.conf")     
                fw = open('log2.txt', 'a')
                fw.write('try to reconnect via supplicant' +'\n')
                fw.close()       

    if is_connected():
        print('already connected')
    if testmod or not is_connected():
        print('try to connect:')
        fw = open('log2.txt', 'a')
        fw.write('try to connect' +'\n')
        fw.close()
        timestamp = -1
        continue_search=True
        last_check_time = time.time()
        while continue_search:
            was_read, image = cap.read()
            if time.time()-timestamp>20:
                data = decode(image)
                if len(data) > 0:
                    #print("Decoded Data : {}".format(data[0].data))
                    s = data[0].data.decode("utf-8").split(';')
                    pas = ''
                    ssid = ''
                    for i in s:
                        if len(i)>0:
                            if i[0]=='P':
                                pas = i[2:]
                            if i[0]=='S':
                                ssid= i[2:]
                    if pas!='' and ssid!='':
                        text = "network={\n"
                        text+="""ssid="{}"
                    psk="{}"
                    proto=RSN
                    key_mgmt=WPA-PSK
                    pairwise=CCMP
                    auth_alg=OPEN""".format(ssid,pas)
                        text+="\n}"
                        text_file = open("wpa_supplicant_auto.conf", "w")
                        n = text_file.write(text)
                        text_file.close()
                        if Platform=='RPiOS' or Platform=='UNIX':
                            script.reconnect("wpa_supplicant_auto.conf")
                        timestamp=time.time()
                        print("Detected!")
                        if testmod:
                            continue_search=False
                else:
                    print("NotFound")
            else:
                time.sleep(1)
                if not testmod:
                    continue_search = not is_connected()
            cv2.putText(image, 'Show_me_QR_Code_for_WiFi', (320, 240), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255),
                        1)
            if Platform!='RPiOS':
                cv2.imshow("programm", image)
                cv2.waitKey(10)
            else:
                if not testmod:
                    if time.time() - last_check_time>5:
                        continue_search = not is_connected()
                        last_check_time = time.time()
                        fw = open('log2.txt', 'a')
                        fw.write('connected on search' +'\n')
                        fw.close()                        
                if Video:
                    cv2.imshow("programm", image)
                    cv2.waitKey(10)
    else:
        text_file = open("Sucess.txt", "w")
        n = text_file.write('everything ok')
        text_file.close()


    continue_search=True
    timestamp = -1
    if not os.path.isfile("tg_creedential.txt"):
        while continue_search:
            was_read, image = cap.read()
            if time.time() - timestamp > 10:
                data = decode(image)
                if len(data) > 0:
                    s = data[0].data.decode("utf-8").split('\n')
                    if len(s)==4:
                        text_file = open("tg_creedential.txt", "w")
                        for i in s:
                            n = text_file.write(i + '\n')
                        text_file.close()
                        timestamp = time.time()
                        continue_search=False
            cv2.putText(image, 'Show_me_QR_Code_for_Telegramm', (320, 240), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255),
                            1)
            cv2.imshow("programm", image)
            cv2.waitKey(10)