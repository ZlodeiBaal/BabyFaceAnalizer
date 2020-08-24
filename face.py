#!/usr/bin/env python
import cv2
import numpy as np
from openvino.inference_engine import IECore
import time
import random, string
import os
import DetectionModels, DrawFunctions, StateMachine, telegram_reports
import webrtcvad
import pyaudio

RPicamera = False

def LoadData(folder_load):
    image_files=[]
    for j in range(200):
        adress = os.path.join(folder_load, str(j)+'.jpg')
        if os.path.isfile(adress):
            image_files.append(adress)
        else:
            break
    return image_files


if RPicamera:
    from picamera.array import PiRGBArray
    from picamera import PiCamera

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

OutputDirections = False
DetectEyes = True
DrawOnImage = True
ShowImage = True
last_time_eye_save = -1
save_eye = True
Video=True

def DecideParams(ie):
    Device_List = ie.available_devices
    DeviceName =""
    Platform=''
    try:
        if os.uname()[4][:3] == 'arm':
            print('RPi found')
            if 'MYRIAD' in Device_List:
                DeviceName = 'MYRIAD'
                Platform='RPiOS'
                print('MYRIAD found')
            else:
                DeviceName = 'None'
                Platform='RPiOS'
                print('MYRIAD NOT found - everything will not work')
        else:
            print('CPU found, unix')
            if 'CPU' in Device_List:
                DeviceName = 'CPU'
                Platform = 'UNIX'
                print('CPU found, unix')
            else:
                DeviceName = 'None'
                Platform='UNIX'
                print('CPU NOT found, unix - everything will not work ')
    except:
        if 'CPU' in Device_List:
            DeviceName = 'CPU'
            Platform = 'WIN'
            print('CPU found, win')
        else:
            DeviceName = 'None'
            Platform = 'WIN'
            print('CPU NOT found, WIN - everything will not work ')

    return DeviceName, Platform



def main():

    #AudioPart
    Audio=False
    try:
        CHUNK = 480
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 1
        p = pyaudio.PyAudio()
        stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    input_device_index = 0,
                    frames_per_buffer = CHUNK)
        vad = webrtcvad.Vad()
        vad.set_mode(3)
        Audio=True
    except Exception:
        print("exeption, no audio")



    images_angry = LoadData("./Images/angry/")
    print('loaded angry - '+str(len(images_angry)))
    images_happy = LoadData("./Images/happy/")
    images_neutral = LoadData("./Images/neutral/")
    images_sad = LoadData("./Images/sad/")
    images_surprise = LoadData("./Images/surprise/")
    angry_pos=0
    happy_pos=0
    neutral_pos=0
    sad_pos=0
    surprise_pos=0
    time_now = time.time()
    time_last = time.time()

    ie = IECore()
    DeviceName, Platform = DecideParams(ie)

    rtsp = "rtsp://192.168.0.87/stream0"
    if Platform=='RPiOS':
        DrawOnImage = True
        ShowImage = False
        last_time_eye_save = -1
        save_eye = True
        USBCam=True
        Video = True
    else:
        DrawOnImage = True
        ShowImage = True
        last_time_eye_save = -1
        save_eye = True
        USBCam = True
        Video = True
    if Video:
        cv2.namedWindow("Main", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Main", cv2.WND_PROP_FULLSCREEN, 1)
    SM = StateMachine.State()
    Tel = telegram_reports.BOT()

    FaceDetector = DetectionModels.FaceDetectModel(ie,DeviceName,Platform)
    FaceLMDetector = DetectionModels.FacePointModel(ie,DeviceName,Platform)
    FaceEmotionDetector = DetectionModels.FaceExpressionModel(ie,DeviceName,Platform)
    FaceOrientDetector = DetectionModels.FaceOrientationModel(ie,DeviceName,Platform)
    EyeOrientationDetector = DetectionModels.EyeOrientationModel(ie,DeviceName,Platform)
    EyeType = DetectionModels.EyeTypeModel(ie,DeviceName,Platform)


    if RPicamera:
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.1)
    else:
        if USBCam:
            cap = cv2.VideoCapture(0)
        else:
            cap = cv2.VideoCapture(rtsp)

    while True:
        if RPicamera:
            rawCapture.truncate(0)
            image = next(camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)).array
        else:
            was_read, image = cap.read()
            if not USBCam:
                image = cv2.resize(image,(640,360))
        (input_height, input_width) = image.shape[:-1]
        input_image = image.copy()
        input_image_raw = image.copy()
        disp = FaceDetector.PredictFace(image)

        isFaceFound = False
        
        if Audio:
                data_audio = stream.read(CHUNK, exception_on_overflow = False)   
                result_audio = vad.is_speech(data_audio, RATE)
                #if result_audio:
                #    print('Kek_')
        else:
            result_audio=False
        for j in range(disp.shape[0]):
            hypotesis = disp[j]
            if hypotesis[2]>0.8:
                isFaceFound=True
                emo = 'neutral'
                vec1='NotPresent'
                vec2='NotPresent'
                emo_disp = np.zeros(5)
                (pitch, roll, yaw) = (0,0,0)
                (vec, gazeAnglesx, gazeAnglesy) = (0,0,0)
                xtl = (int)(hypotesis[3]*input_width)
                ytl = (int)(hypotesis[4] * input_height)
                xbr = (int)(hypotesis[5]*input_width)
                ybr = (int)(hypotesis[6] * input_height)
                img = input_image_raw[ytl:ybr,xtl:xbr,:]
                (input_h, input_w) = img.shape[:-1]
                if input_h>5 and input_w>5:
                    disp2 = FaceLMDetector.PredictPoints(img)
                    emo, emo_disp = FaceEmotionDetector.PredictExpression(img)
                    pitch, roll, yaw = FaceOrientDetector.PredictOrientation(img)

                    if DrawOnImage:
                        cv2.rectangle(input_image,(xtl,ytl),(xbr,ybr),(255,0,0),2)
                        input_image = DrawFunctions.draw_axis(input_image,yaw,pitch,roll,(int)((xtl+xbr)/2),(int)((ytl+ybr)/2))
                        for i in range(5):
                            point_x = disp2[i*2][0][0]
                            point_y = disp2[i * 2+1][0][0]
                            cv2.circle(input_image, ((int)(xtl+point_x*input_w), (int)(ytl+point_y*input_h)), 1, (255, 0, 0), 2)
                            cv2.putText(input_image,emo, (xtl,ybr),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)

                    if DetectEyes:

                        xmidl = (int)(xtl+disp2[0][0][0]*input_w)
                        ymidl = (int)(ytl+disp2[1][0][0]*input_h)
                        widthl = (int)(input_w/4)
                        w2l = (int)(widthl/2)

                        xmidr = (int)(xtl + disp2[2][0][0] * input_w)
                        ymidr = (int)(ytl + disp2[3][0][0] * input_h)
                        widthr = widthl
                        w2r = (int)(widthr / 2)
                        if w2l>5 and w2r>5 and xmidl - w2l>0 and xmidl + w2l<input_width and ymidl - w2l>0 and ymidl + w2l<input_height and ymidr - w2r>0 and ymidr + w2r<input_height and xmidr - w2r>0 and xmidr + w2r<input_width:


                            img_left_eye = input_image_raw[ymidl - w2l:ymidl + w2l, xmidl - w2l:xmidl + w2l, :]
                            img_right_eye = input_image_raw[ymidr - w2r:ymidr + w2r, xmidr - w2r:xmidr + w2r, :]

                            vec1 = EyeType.PredictType(img_left_eye)
                            vec2 = EyeType.PredictType(img_right_eye)
                            #print(vec1)
                            #print(vec2)
                            '''
                            if time.time()-last_time_eye_save>1 and save_eye:
                                last_time_eye_save=time.time()
                                name = randomString(8)
                                cv2.imwrite('./EyeDataset/'+name+'_left.jpg',img_left_eye)
                                cv2.imwrite('./EyeDataset/' + name + '_right.jpg', img_right_eye)
                            '''
                            vec, gazeAnglesx, gazeAnglesy = EyeOrientationDetector.PredictOrientation(img_left_eye,img_right_eye,pitch,roll,yaw)
                            if DrawOnImage:
                                if abs(gazeAnglesx)<5 and abs(gazeAnglesy)<5:
                                    cv2.rectangle(input_image, (xtl, ytl), (xbr, ybr), (0, 255, 0), 2)
                            if OutputDirections:
                                print(str(gazeAnglesx)+"      "+str(gazeAnglesy))
        if isFaceFound:
            if DetectEyes:
                SM.append(True,(xtl,ytl),(input_w,input_h),emo,(pitch, roll, yaw),(vec, gazeAnglesx, gazeAnglesy),emo_disp,(vec1,vec2),result_audio)
            else:
                SM.append(True, (xtl, ytl), (input_w, input_h), emo, (pitch, roll, yaw),
                          ([0,0,0], 0, 0),emo_disp,('NotPresent','NotPresent'),result_audio)
        else:
            SM.append(False, (0, 0), (0, 0), 'neutral', (0, 0, 0), ([0,0,0], 0, 0),(0,0,0,0,0),('NotPresent','NotPresent'),result_audio)



        Tel.ReleaseRequests(SM,input_image)
        if ShowImage:
            cv2.imshow("depth",input_image)
            cv2.waitKey(10)
        if Video:
            blank_image = np.zeros((480, 640, 3), np.uint8)
            if Tel.GameMode:
                time_now = time.time()
                dt = (time_now-time_last)*30
                sdvig=1
                if dt==0:
                    sdvig=1
                else:
                    if dt>10:
                        sdvig=10
                    else:
                        sdvig=int(dt)

                if SM.FrameList[-1].Emotion=='anger':
                    #blank_image=cv2.imread('./Images/sun.jpg')
                    #blank_image=cv2.imread('./Images/happy.jpg')
                    blank_image=cv2.imread(images_angry[angry_pos])
                    angry_pos+=sdvig
                    if angry_pos>=len(images_angry):
                        angry_pos=0
                if SM.FrameList[-1].Emotion=='happy':
                    #blank_image=cv2.imread('./Images/lightning.jpg')
                    #blank_image=cv2.imread('./Images/sad.jpg')
                    blank_image=cv2.imread(images_happy[happy_pos])
                    happy_pos+=sdvig
                    if happy_pos>=len(images_happy):
                        happy_pos=0
                if SM.FrameList[-1].Emotion=='neutral':
                    #blank_image=cv2.imread('./Images/tree.jpg')
                    #blank_image=cv2.imread('./Images/surpryze.jpg')
                    blank_image=cv2.imread(images_neutral[neutral_pos])
                    neutral_pos+=sdvig
                    if neutral_pos>=len(images_neutral):
                        neutral_pos=0
                if SM.FrameList[-1].Emotion=='sad':
                    #blank_image=cv2.imread('./Images/lightning.jpg')
                    #blank_image=cv2.imread('./Images/angry.jpg')
                    blank_image=cv2.imread(images_sad[sad_pos])
                    sad_pos+=sdvig
                    if sad_pos>=len(images_sad):
                        sad_pos=0
                if SM.FrameList[-1].Emotion=='surprise':
                    #blank_image=cv2.imread('./Images/cherniy_kvadrat.jpg')
                    #blank_image=cv2.imread('./Images/neutral.jpg')
                    blank_image=cv2.imread(images_surprise[surprise_pos])
                    surprise_pos+=sdvig
                    if surprise_pos>=len(images_surprise):
                        surprise_pos=0
                time_last  = time_now
            else:
                cv2.putText(blank_image,'GameModIsOff', (320,240),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
            cv2.imshow("Main",blank_image)
            cv2.waitKey(10)


if __name__ == '__main__':
    main()
