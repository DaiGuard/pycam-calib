#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2
import subprocess
import re
import numpy as np

capture_device = None
store_images = []
store_mtx = None
store_dist = None


def open_device(id, format):
    # グローバル変数
    global capture_device

    # 開き済みのデバイスを閉じる
    if capture_device is not None:
        capture_device.release()

    capture_device = cv2.VideoCapture(id)
    capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, format[0])
    capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, format[1])

def close_device():
    # グローバル変数
    global capture_device

    capture_device.release()    
    capture_device = None


def get_frame(width=0, height=0):
    # グローバル変数
    global capture_device, store_mtx, store_dist

    if capture_device:
        ret, frame = capture_device.read()        
        if ret:
            if store_mtx is not None and store_dist is not None:
                # h, w = frame.shape[:2]
                # newcameramtx = cv2.getOptimalNewCameraMatrix(store_mtx, store_dist,
                #     (w, h), 1, (w, h))
                frame = cv2.undistort(frame, store_mtx, store_dist)

            if width > 0 and height > 0:
                frame = cv2.resize(frame, (width, height))
            return frame
    
    return None

def store_image(image):
    # グローバル変数
    global store_images

    store_images.append(image)

    return len(store_images)


def get_store_image_num():
    # グローバル変数
    global store_images

    return len(store_images)

def resize(image, w, h):
    return cv2.resize(image, (w, h))


def draw_chessbord(image, h, v, width=0, height=0):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (h, v), None)
    if ret:
        draw_image = cv2.drawChessboardCorners(image, (h, v), corners, ret)
        if width > 0 and height > 0:
            draw_image = cv2.resize(draw_image, (width, height))
        return draw_image

    return None


def is_calibrated():
    # グローバル変数
    global store_mtx, store_dist

    if store_mtx is not None and store_dist is not None:
        return True

    return False


def save_calib(path):
    # グローバル変数
    global store_mtx, store_dist

    if store_mtx is not None and store_dist is not None:
        np.save(os.path.join(path, 'mtx'), store_mtx)
        np.save(os.path.join(path, 'dist'), store_dist)


def calc_calib(h, v, size):
    # グローバル変数
    global store_images, store_mtx, store_dist

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    image_points = []
    object_points = []
    image_shape = None
    obj = np.zeros((np.prod((h, v)), 3), np.float32)
    obj[:,:2] = np.indices((h, v)).T.reshape(-1, 2)
    obj *= size / 10.0


    for image in store_images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_shape = gray.shape
        ret, corners = cv2.findChessboardCorners(gray, (h, v), None)
        if ret:
            corners_sub = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), criteria)                
            image_points.append(corners_sub)
            object_points.append(obj)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        object_points, image_points, image_shape[::-1], None, None)

    # キャリブレーション結果を保存
    store_mtx = mtx
    store_dist = dist


def get_device_list() -> dict:
    """get camera device list

    Returns:
        list: camera device file name list,
            ex. ["/dev/video0 (Web Camera)", ...]
    """

    result = subprocess.run([
        'v4l2-ctl',
        '--list-devices'
        ],
        stdout=subprocess.PIPE,
        text=True,
        timeout=3.0,
    )

    device_list = {}

    if result.returncode == 0:        
        # デバイスごとに分割
        devices = result.stdout.split('\n\n')

        # デバイスごとにデータを読み解く
        for device in devices:

            device_info = device.split('\n')
            device_file_num = len(device_info) - 1

            if device_file_num > 0:
                device_name = device_info[0].rstrip('\n').rstrip(':')

                for i in range(1, device_file_num+1):
                    path = device_info[i].lstrip('\t').rstrip('\n')
                    index = int(re.sub(r'\D', '', path))
                    device_list[index] = (path, device_name)
        
    return device_list


def get_format_list() -> dict:
    """get format list

    Returns:
        list: camera format list,
            ex. [(yuvu, [(1280,640,30.0),...]), ...]
    """

    result = subprocess.run([
        'v4l2-ctl',
        '--list-formats-ext'
        ],
        stdout=subprocess.PIPE,
        text=True,
        timeout=3.0,
    )

    format_list = {}

    if result.returncode == 0:
        # デバイスごとに分割
        devices = result.stdout.split('\n\n')

        try:        
            for device in devices:
                
                index = -1
                size = []

                for line in device.split('\n'):
                    element = line.lstrip('\t').lstrip('\n').split(':')
                    name = element[0].lstrip(' ').rstrip(' ')
                    value = element[1].lstrip(' ').rstrip(' ')                

                    if name == 'Index':
                        index = int(value)
                    elif name == 'Size':
                        value = value.split(' ')[1].split('x')
                        size.append((int(value[0]),int(value[1])))

                if index >= 0 and len(size) > 0:
                    format_list[index] = size

        except IndexError as ex:
            pass

    return format_list


if __name__ == '__main__':

    device_list = get_device_list()
    print(device_list)

    format_list = get_format_list()
    print(format_list)