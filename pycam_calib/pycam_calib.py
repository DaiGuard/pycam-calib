#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from utils import camera_utils


__appname__ = 'pycam-calib'


class MainWindow(QMainWindow):    


    def __init__(self):
        super().__init__()

        # 変数登録        
        self.device_id = -1
        self.device_format = (0, 0)
        self.temp_image = None
        
        # UIデータの読み込み
        self.ui = uic.loadUiType('resource/pycam_calib.ui', self)[0]()
        self.ui.setupUi(self)        

        # カメラデバイス名の登録
        self.updateDeviceList()

        # 画面色の初期化
        black_pix = QPixmap(self.ui.maincam_label.size())
        black_pix.fill(QColor(0, 0, 0))
        self.ui.maincam_label.setPixmap(black_pix)

        black_pix = QPixmap(self.ui.capture_label.size())
        black_pix.fill(QColor(0, 0, 0))
        self.ui.capture_label.setPixmap(black_pix)

        # シグナル・スロットの登録 
        self.ui.device_box.currentIndexChanged.connect(self.selectDevice)
        self.ui.format_box.currentIndexChanged.connect(self.selectFormat)
        self.ui.device_open_btn.clicked.connect(self.openDevice)
        self.ui.capture_btn.clicked.connect(self.captureImage)
        self.ui.store_btn.clicked.connect(self.storeImage)
        self.ui.calc_btn.clicked.connect(self.calcCalibration)
        self.ui.save_btn.clicked.connect(self.saveCalibration)

        # ループ処理
        self.startTimer(30)


    def saveCalibration(self, checked):
        if camera_utils.is_calibrated():
            path = QFileDialog.getExistingDirectory(None, "保存するフォルダを選んでください")
            camera_utils.save_calib(path)

            self.statusBar().showMessage('Success save calibration parameters')
        else:
            self.statusBar().showMessage('not calculate calibration parameters')


    def calcCalibration(self, checked):
        if camera_utils.get_store_image_num() < 20:
            self.statusBar().showMessage('Not enough images for calculation 20')
        else:
            corner_h = self.ui.corner_h_box.value()
            corner_v = self.ui.corner_v_box.value()
            corner_size = self.ui.corner_size_box.value()

            camera_utils.calc_calib(corner_h, corner_v, corner_size)

            self.statusBar().showMessage('Success calclate calibration parameters')


    def captureImage(self, checked):
        frame = camera_utils.get_frame()
        self.temp_image = frame

        corner_h = self.ui.corner_h_box.value()
        corner_v = self.ui.corner_v_box.value()

        size = self.ui.capture_label.size()
        image = camera_utils.draw_chessbord(
                    frame, corner_h, corner_v,
                    size.width(), size.height())        
        if image is not None:
            img = QImage(image.tobytes(), 
                image.shape[1], image.shape[0], image.strides[0],
                QImage.Format.Format_BGR888)
            pix = QPixmap.fromImage(img)
            self.ui.capture_label.setPixmap(pix)


    def storeImage(self, checked):
        if self.temp_image is not None:
            num = camera_utils.store_image(self.temp_image)
            resize_image = camera_utils.resize(self.temp_image, 160, 120)
            qimg = QImage(resize_image.tobytes(),
                resize_image.shape[1], resize_image.shape[0], resize_image.strides[0],
                QImage.Format.Format_BGR888)
            qpix = QPixmap.fromImage(qimg)            
            label = QLabel()            
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            label.setFixedSize(160, 120)
            label.setPixmap(qpix)
            
            self.ui.store_label.setText(f'{num} store')
            self.ui.image_list_layout.addWidget(label)

            self.temp_image = None


    def timerEvent(self, event):
        size = self.ui.maincam_label.size()
        frame = camera_utils.get_frame(size.width(), size.height())
        if frame is not None:
            img = QImage(frame.tobytes(), 
                frame.shape[1], frame.shape[0], frame.strides[0],
                QImage.Format.Format_BGR888)
            pix = QPixmap.fromImage(img)
            self.ui.maincam_label.setPixmap(pix)


    def openDevice(self, checked):
        if self.device_id >= 0 and self.device_format != (0, 0):
            camera_utils.open_device(
                self.device_id, self.device_format)


    def updateDeviceList(self):        
        device_list = camera_utils.get_device_list()
        self.ui.device_box.clear()
        self.ui.device_box.addItem('', -1)
        for key, value in device_list.items():
            self.ui.device_box.addItem(f'{value[0]} ({value[1]})' , key)


    def selectDevice(self, id):
        data = self.ui.device_box.itemData(id)
        self.device_id = data
        self.updateFormatList(self.device_id)


    def updateFormatList(self, id):
        format_list = camera_utils.get_format_list()
        self.ui.format_box.clear()
        self.ui.format_box.addItem('', (0, 0))
        if id in format_list:
            formats = format_list[id]
            for fmt in formats:
                self.ui.format_box.addItem(f'{fmt[0]}x{fmt[1]}', fmt)        


    def selectFormat(self, id):
        data = self.ui.format_box.itemData(id)
        self.device_format = data        


def main(argv=None):

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    sys.exit(main())