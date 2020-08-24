from collections import namedtuple
import time
import numpy as np


class State():
    history_to_manage = 60 #sec
    IsFaceStableSeen = False
    IsAudio=False
    IsNormalSeen = True
    IsSleep = True
    Face_detection_interval = 30#sec
    Emo_interval = 5
    How_Offten_spam = 60#sec
    Pending_for_alarm = False
    disp_main=0
    Emo_alarm='neutral'
    alarm_type=[]
    FrameList = []
    Last_Time_sent = -1
    Last_Time_sent_sleep = -1
    Last_Time_sent_rotation = -1
    Last_Time_sent_Eyes = -1
    Last_Time_sent_Audio = -1
    rotation_time = 0
    EyesOpened = 0

    def __init__(self):
        self.Frame = namedtuple("FrameData", "isFace Time FacePose FaceSize Emotion FaceDirection EyeDirection EyeStatus Audio")

    def calculate_face_vizibilty(self):
        not_seen = 0
        seen = 0
        events=0
        timenow = time.time()
        for j in range(len(self.FrameList)):
            if (timenow-self.FrameList[j].Time)<self.Face_detection_interval:
                events+=1
                F = self.FrameList[j]
                if not F.isFace:
                    not_seen+=1
                else:
                    seen+=1
        if events>10:
            if not_seen*3>=seen:
                if self.IsFaceStableSeen:
                    self.IsFaceStableSeen=False
                    if timenow - self.Last_Time_sent>self.How_Offten_spam:
                        self.Pending_for_alarm = True
                        self.alarm_type.append(0)
            else:
                if seen>not_seen/2:
                    self.IsFaceStableSeen = True

    def calculate_face_mood(self):
        normal = 0
        notnormal = 0
        timenow = time.time()
        states = ['happy', 'sad', 'surprise', 'anger']
        st = {states[0]:0, states[1]:1, states[2]:2, states[3]:3}
        amount = [0,0,0,0]
        for j in range(len(self.FrameList)):
            if (timenow-self.FrameList[j].Time)<self.Emo_interval:
                F = self.FrameList[j]
                if F.Emotion=='neutral':
                    normal+=1
                else:
                    amount[st[F.Emotion]]+=1
                    notnormal+=1
        if normal<=notnormal:
            if self.IsNormalSeen:
                self.IsNormalSeen=False

                if timenow - self.Last_Time_sent>self.How_Offten_spam:
                    self.Pending_for_alarm = True
                    self.Emo_alarm = states[np.argmax(np.array(amount))]
                    self.alarm_type.append(1)
                    self.Last_Time_sent = timenow
        else:
            if notnormal==0:
                self.IsNormalSeen = True

    def calculate_open_eyes(self):
        okno = 50
        porog = 20
        count=0
        amount=0
        timenow = time.time()
        if len(self.FrameList) > okno:
            for j in range(okno):
                if (timenow - self.FrameList[-j].Time) < 40:
                    amount+=1
                    if self.FrameList[-j].EyeStatus[0]=='Opened':
                        count+=1
                    if self.FrameList[-j].EyeStatus[1]=='Opened':
                        count+=1
        if amount>4*okno/5 and count>porog:
            if self.EyesOpened==0:
                self.EyesOpened=1
                if timenow - self.Last_Time_sent_Eyes > self.How_Offten_spam:
                    self.alarm_type.append(3)
                    self.Pending_for_alarm = True
                    self.Last_Time_sent_Eyes = timenow
        else:
            self.EyesOpened = 0

    def calculate_audio(self):
        okno = 10
        timenow = time.time()
        amount=0
        if len(self.FrameList) > okno:
            for j in range(okno):
                if self.FrameList[-j].Audio:
                    amount+=1
        if amount>2:
            self.isAudio=True
            if timenow - self.Last_Time_sent_Audio > self.How_Offten_spam:
                self.alarm_type.append(4)
                #print('Here')
                self.Pending_for_alarm = True
                self.Last_Time_sent_Audio = timenow
        else:
            self.isAudio=False



    def calculate_face_rotation(self):
        normal = 0
        notnormal = 0
        timenow = time.time()
        okno = 180
        porog = 20
        if len(self.FrameList)>okno:
            mean_roll = 0
            mean_pitch = 0
            mean_yaw = 0
            for j in range(okno):
                mean_pitch+=self.FrameList[-j].FaceDirection[0]
                mean_roll += self.FrameList[-j].FaceDirection[1]
                mean_yaw += self.FrameList[-j].FaceDirection[2]
            mean_pitch = mean_pitch/okno
            mean_roll=mean_roll/okno
            mean_yaw=mean_yaw/okno
            disp_pitch=0
            disp_roll=0
            disp_yaw =0
            for j in range(okno):
                disp_pitch+=abs(self.FrameList[-j].FaceDirection[0]-mean_pitch)
                disp_roll += abs(self.FrameList[-j].FaceDirection[1]-mean_roll)
                disp_yaw += abs(self.FrameList[-j].FaceDirection[2]-mean_yaw)
            disp_pitch = disp_pitch/okno
            disp_roll=disp_roll/okno
            disp_yaw=disp_yaw/okno
            disp_summ = disp_pitch+disp_roll+disp_yaw
            self.disp_main=disp_summ

            if disp_summ>porog:
                if self.IsSleep:

                    #print(self.rotation_time)
                    if self.rotation_time > 10:
                        self.rotation_time =0
                        self.IsSleep = False
                        if timenow - self.Last_Time_sent_rotation>self.How_Offten_spam:
                            self.Pending_for_alarm = True
                            self.Last_Time_sent_rotation = timenow
                            self.alarm_type.append(2)
                    else:
                        self.rotation_time+=1
            else:
                self.IsSleep = True


    def append(self,state,pos,size,emo,ang,eye,emo_disp, ES,audio):
        #fw = open('log.txt', 'a')
        #fw.write(str(state) + '\t' + str(pos)+ '\t' + str(size) + '\t' + str(emo)+ '\t' +str(emo_disp)+'\t'+str(ang) + '\t' + str(eye) +'\n')
        #fw.close()

        F = self.Frame(state,time.time(),pos,size,emo,ang,eye,ES,audio)
        self.FrameList.append(F)
        timenow=time.time()
        j=0
        while j<len(self.FrameList):
            if (timenow-self.FrameList[j].Time)>self.history_to_manage:
                self.FrameList.pop(j)
            else:
                j+=1
        self.calculate_face_vizibilty()
        self.calculate_face_mood()
        self.calculate_face_rotation()
        self.calculate_open_eyes()
        self.calculate_audio()