import cv2 #OpenCV in my opinion best library for work with camera
from pyzbar.pyzbar import decode #Zbar - best opensource library for work with QRcode. OpenCV also can it, but not in every build.
import socket
import time
import os
import script

RPicamera = False #also can work with RPiCamera
if RPicamera:
    from picamera.array import PiRGBArray
    from picamera import PiCamera


#ForTestReasons
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

#Simple check if internet is online
def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

#Check if ARM
Platform = DecideParams()
testmod = True #To test on Windows machine without connections


if Platform=='RPiOS' or Platform=='UNIX' or testmod:
    isconnect=False
    #Try to connect for 60 seconds. If no connection found - start process
    if not testmod:
        time_start = time.time()
        isconnect = is_connected()
        try_to_connect = not isconnect
        while try_to_connect:
            time.sleep(5)
            if time.time()-time_start<60:
                try_to_connect=False
            if is_connected():
                try_to_connect=False
    #if machine not connected to internet or in testmode
    if testmod or not isconnect:
        #if we have RPi camera - we can use it
        if RPicamera:
            camera = PiCamera()
            camera.resolution = (640, 480)
            camera.framerate = 32
            rawCapture = PiRGBArray(camera, size=(640, 480))
            time.sleep(0.1)
        else:
            cap = cv2.VideoCapture(0)

        timestamp = -1
        continue_search=True
        last_check_time = time.time()
        while continue_search:
            #if we have RPI camera
            if RPicamera:
                rawCapture.truncate(0)
                image = next(camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)).array
            else:
                was_read, image = cap.read()
            #After we find QRCode - we stop deterction for 20 secondes, or it will be continius reconnect attemps
            if time.time()-timestamp>20:
                data = decode(image) #Search for codes
                if len(data) > 0:
                    #Parse classical QRCode structure for WiFi connection
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
                        #Create connection file wor wpa
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
                else:
                    print("NotFound")
            else:
                time.sleep(1)
                if not testmod:
                    continue_search = not is_connected()
            if Platform!='RPiOS': # if not RPi - visualisation
                cv2.imshow("depth", image)
                cv2.waitKey(10)
            else:
                if not testmod: # if not testmode - try to connect
                    if time.time() - last_check_time>5:
                        continue_search = not is_connected()
                        last_check_time = time.time()