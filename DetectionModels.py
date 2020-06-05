from math import cos, sin, fabs, pi, atan2, acos
import cv2
import numpy as np
import time
from openvino.inference_engine import IENetwork

OutputTimes = False

def PrepareImage(image,width,height):
    image = cv2.resize(image, (width, height), cv2.INTER_CUBIC)
    # prepare input
    image = image.astype(np.float32)
    image = image.transpose((2, 0, 1))
    image_input = np.expand_dims(image, 0)
    return image_input

class FaceDetectModel():
    model_xml = "./Models/face-detection-adas-0001.xml"
    model_bin = "./Models/face-detection-adas-0001.bin"
    def __init__(self, ie, DeviceName,Platform):
        try:
            if Platform!='RPiOS':
                self.net = ie.read_network(model=self.model_xml, weights=self.model_bin)
            else:
                self.net = IENetwork(model=self.model_xml, weights=self.model_bin)
            self.input_blob = next(iter(self.net.inputs))
            self.out_blob = next(iter(self.net.outputs))
            self.net.batch_size = 1
            _, _, self.height, self.width = self.net.inputs[self.input_blob].shape
            self.exec_net = ie.load_network(network=self.net, device_name=DeviceName)
            print('Face Model load sucess')
        except Exception:
            print(Exception)
            print('Face Model load unsucess')

    def PredictFace(self,image):
        # resize
        image_input = PrepareImage(image, self.width, self.height)
        start = time.time()
        res = self.exec_net.infer(inputs={self.input_blob: image_input})
        end = time.time()
        if OutputTimes:
            print(end - start)
        return res[self.out_blob][0][0]

class FacePointModel():
    model_xml = "./Models/landmarks-regression-retail-0009.xml"
    model_bin = "./Models/landmarks-regression-retail-0009.bin"

    def __init__(self, ie, DeviceName,Platform):
        try:
            if Platform != 'RPiOS':
                self.net = ie.read_network(model=self.model_xml, weights=self.model_bin)
            else:
                self.net = IENetwork(model=self.model_xml, weights=self.model_bin)
            self.input_blob = next(iter(self.net.inputs))
            self.out_blob = next(iter(self.net.outputs))
            self.net.batch_size = 1
            _, _, self.height, self.width = self.net.inputs[self.input_blob].shape
            self.exec_net = ie.load_network(network=self.net, device_name=DeviceName)
            print('Face point Model load sucess')
        except:
            print('Face point Model load UNsucess')

    def PredictPoints(self, image):
        # resize
        image_input = PrepareImage(image, self.width, self.height)
        start = time.time()
        res = self.exec_net.infer(inputs={self.input_blob: image_input})
        end = time.time()
        if OutputTimes:
            print(end - start)
        return res[self.out_blob][0]

class FaceExpressionModel():
    model_xml = "./Models/emotions-recognition-retail-0003.xml"
    model_bin = "./Models/emotions-recognition-retail-0003.bin"
    states = ('neutral', 'happy', 'sad', 'surprise', 'anger')
    def __init__(self, ie, DeviceName,Platform):
        try:
            if Platform != 'RPiOS':
                self.net = ie.read_network(model=self.model_xml, weights=self.model_bin)
            else:
                self.net = IENetwork(model=self.model_xml, weights=self.model_bin)
            self.input_blob = next(iter(self.net.inputs))
            self.out_blob = next(iter(self.net.outputs))
            self.net.batch_size = 1
            _, _, self.height, self.width = self.net.inputs[self.input_blob].shape
            self.exec_net = ie.load_network(network=self.net, device_name=DeviceName)
            print('Face expression Model load sucess')
        except:
            print('Face expression Model load UNsucess')

    def PredictExpression(self, image):
        # resize
        image_input = PrepareImage(image, self.width, self.height)
        start = time.time()
        res = self.exec_net.infer(inputs={self.input_blob: image_input})
        end = time.time()
        if OutputTimes:
            print(end - start)
        disp = res[self.out_blob][0].reshape(5)
        return self.states[np.argmax(disp)],disp

class FaceOrientationModel():
    model_xml = "./Models/head-pose-estimation-adas-0001.xml"
    model_bin = "./Models/head-pose-estimation-adas-0001.bin"

    def __init__(self, ie, DeviceName,Platform):
        try:
            if Platform != 'RPiOS':
                self.net = ie.read_network(model=self.model_xml, weights=self.model_bin)
            else:
                self.net = IENetwork(model=self.model_xml, weights=self.model_bin)
            self.input_blob = next(iter(self.net.inputs))
            self.out_blob = next(iter(self.net.outputs))
            self.net.batch_size = 1
            _, _, self.height, self.width = self.net.inputs[self.input_blob].shape
            self.exec_net = ie.load_network(network=self.net, device_name=DeviceName)
            print('Face orientation Model load sucess')
        except:
            print('Face Orientation Model load UNsucess')

    def PredictOrientation(self, image):
        # resize
        image_input = PrepareImage(image, self.width, self.height)
        start = time.time()
        res = self.exec_net.infer(inputs={self.input_blob: image_input})
        end = time.time()
        if OutputTimes:
            print(end - start)
        pitch = res['angle_p_fc'][0][0]
        roll = res['angle_r_fc'][0][0]
        yaw = res['angle_y_fc'][0][0]
        return pitch, roll, yaw



class EyeTypeModel():
    model_xml = "./fp16/mobilnet.xml"
    model_bin = "./fp16/mobilnet.bin"
    types=['Closed','NotPresent','Opened']
    def __init__(self, ie, DeviceName,Platform):
        try:
            if Platform != 'RPiOS':
                self.net = ie.read_network(model=self.model_xml, weights=self.model_bin)
            else:
                self.model_xml = "./fp16_RPI/mobilnet.xml"
                self.model_bin = "./fp16_RPI/mobilnet.bin"
                self.net = IENetwork(model=self.model_xml, weights=self.model_bin)
            self.input_blob = next(iter(self.net.inputs))
            self.out_blob = next(iter(self.net.outputs))
            self.net.batch_size = 1
            _, _, self.height, self.width = self.net.inputs[self.input_blob].shape
            self.exec_net = ie.load_network(network=self.net, device_name=DeviceName)
            print('EyeTypeModel load sucess')
        except:
            print('EyeTypeModel load UNsucess')

    def PredictType(self, image):
        # resize
        image_input = PrepareImage(image, self.width, self.height)/(255.0)
        start = time.time()
        res = self.exec_net.infer(inputs={self.input_blob: image_input})
        end = time.time()
        if OutputTimes:
            print(end - start)
        result = np.argmax((res[self.out_blob][0]))


        return self.types[result]



class EyeOrientationModel():
    model_xml = "./Models/gaze-estimation-adas-0002.xml"
    model_bin = "./Models/gaze-estimation-adas-0002.bin"

    def __init__(self, ie, DeviceName,Platform):
        try:
            if Platform != 'RPiOS':
                self.net = ie.read_network(model=self.model_xml, weights=self.model_bin)
            else:
                self.net = IENetwork(model=self.model_xml, weights=self.model_bin)
            self.net.batch_size = 1
            _, _, self.height, self.width = self.net.inputs['left_eye_image'].shape
            self.exec_net = ie.load_network(network=self.net, device_name=DeviceName)
            print('Eye orientation Model load sucess')
        except:
            print('Eye Orientation Model load UNsucess')

    def PredictOrientation(self, img_left_eye, img_right_eye, pitch, roll, yaw):
        # resize
        img_left_eye = cv2.resize(img_left_eye, (self.width, self.height), cv2.INTER_CUBIC)
        img_right_eye = cv2.resize(img_right_eye, (self.width, self.height), cv2.INTER_CUBIC)

        img_left_eye = img_left_eye.astype(np.float32)
        img_left_eye = img_left_eye.transpose((2, 0, 1))
        img_left_eye = np.expand_dims(img_left_eye, 0)

        img_right_eye = img_right_eye.astype(np.float32)
        img_right_eye = img_right_eye.transpose((2, 0, 1))
        img_right_eye = np.expand_dims(img_right_eye, 0)

        angles = np.zeros((1, 3))
        angles[0][0] = pitch
        angles[0][1] = roll
        angles[0][2] = yaw
        res_eye = self.exec_net.infer(
            inputs={'left_eye_image': img_left_eye, 'right_eye_image': img_right_eye, 'head_pose_angles': angles})
        norma = cv2.norm(res_eye['gaze_vector'])
        vec = res_eye['gaze_vector'][0] / norma

        gazeAnglesx = (180.0 / pi * (pi / 2 + atan2(vec[2], vec[0])))
        gazeAnglesy = (180.0 / pi * (pi / 2 - acos(vec[1])))

        return res_eye['gaze_vector'][0], gazeAnglesx, gazeAnglesy
