import cv2
from PyQt5 import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5 import QtGui
import datetime
import sys
import torch
from matplotlib import pyplot as plt
import numpy as np
import os
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
uiFile_save_video = 'saveGui.Ui'
from_1, base_1 = uic.loadUiType(uiFile_save_video)
#     model = torch.load('"C:/Users/ENVY/Desktop/yolov5"', 'custom',
#                        path='yolov5/runs/train/exp6/weights/best.pt')


def load_model():
    """
    Loads Yolo5 model from pytorch hub.
    :return: Trained Pytorch model.
    """

    model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp6/weights/best.pt',
                           force_reload=True)
    return model


class main_2(QDialog):

    def __init__(self):
        super(main_2, self).__init__()
        loadUi('mainGui.ui', self)
        self.setWindowTitle('Parking DE')
        self.setWindowIcon(QIcon('img/icon.png'))
        self.frame = None
        self.background = True

        self.model = load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

        self.start_buttom.clicked.connect(self.start_show_cctv)
        self.end_buttom.clicked.connect(self.end_show_cctv)
        background = QPixmap('img/1.png')
        self.logo_label.setPixmap(background)
        self.activate_buttom.setCheckable(True)
        self.activate_buttom.toggled.connect(self.car_detection)
        self.car_detection_Enable = False
        self.save_buttom.clicked.connect(self.change_window)

    def change_window(self):
        self.close()
        self.save_Gui = save_Gui()
        self.save_Gui.Bar_proccess()
        self.save_Gui.show()

    def car_detection(self, status):
        if status:
            self.activate_buttom.setText('Stop Detection')
            self.car_detection_Enable = True
        else:
            self.activate_buttom.setText('Activate Detection')
            self.car_detection_Enable = False

    def start_show_cctv(self):
        # 'img/carPark.mp4'
        self.cap = cv2.VideoCapture('img/carPark.mp4')

        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using the model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        # print("def score_frame_first")
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        # print("def class_to_label")
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        # print("def plot_boxes_first")
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        carCounter_empty = 0
        carCounter_full = 0
        lot_number = 0
        # print("def plot_boxes_before_forLoop")
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.3:
                x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape),\
                                 int(row[2] * x_shape), int(row[3] * y_shape)

                empty = (0, 255, 0)
                full = (0, 0, 255)
                if self.class_to_label(labels[i]) == 'Full':
                    cv2.rectangle(frame, (x1, y1), (x2, y2), full, 1)
                    cv2.putText(frame, self.class_to_label(labels[i]),
                                (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, full, 1)
                    cv2.putText(frame, str(lot_number), (x2, y2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, full, 1)
                    carCounter_full += 1
                    lot_number += 1

                elif self.class_to_label(labels[i]) == 'Empty':
                    cv2.rectangle(frame, (x1, y1), (x2, y2), empty, 1)
                    cv2.putText(frame, self.class_to_label(labels[i]),
                                (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, empty, 1)
                    cv2.putText(frame, str(lot_number), (x2, y2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, full, 1)
                    carCounter_empty += 1
                    lot_number += 1
            self.full_output.setText(str(carCounter_full))
            self.empty_output.setText(str(carCounter_empty))
        # print("def plot_boxes_after_forLoop")

        return frame

    def update_frame(self):

        # print("def update_frame")
        ret, self.frame = self.cap.read()
        now = QDate.currentDate()

        current_dat = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")

        self.data_output.setText(current_dat)
        self.time_output.setText(current_time)

        self.frame = cv2.flip(self.frame, 1)

        if self.car_detection_Enable:
            # print("Enable_car_detection_if_1")
            # the program was not working because i forgot to add self. to
            results = self.score_frame(self.frame)
            # the frame
            # print("Enable_car_detection_if_2")
            # the program was not working because i forgot to add self.
            frame = self.plot_boxes(results, self.frame)
            # to the frame
            # print("Enable_car_detection_if_3")
            self.display_video(frame, 1)
            # print("Enable_car_detection_if_4")

        else:
            self.display_video(self.frame, 1)
            # print("Enable_car_detection_else")

    def end_show_cctv(self):
        try:

            self.timer.stop()
            self.cap.release()

        except:

            print("Exiting")

    def display_video(self, frame, window=1):
        qformat = QImage.Format_Indexed8
        if len(frame.shape) == 3:
            if frame.shape[2] == 4:
                # make it into alpha
                qformat = QImage.Format_RGBA8888
            else:
                # assigning the format
                qformat = QImage.Format_RGB888
        outImage = QImage(frame, frame.shape[1], frame.shape[0],
                          frame.strides[0], qformat)
        # BGR >> RGB
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.img_label.setPixmap(QPixmap.fromImage(outImage))
            self.img_label.setScaledContents(True)


class save_Gui(base_1, from_1):
    def __init__(self):
        super(save_Gui, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Saving Video')
        self.setWindowIcon(QIcon('img/save_icon.png'))

    def Bar_proccess(self):
        count_bar = 0

        for i in range(100):
            count_bar += 1
            time.sleep(0.01)
            self.progressBar.setValue(count_bar)
        self.done_label.setText('Error -1073740791 (0xC0000409)')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = main_2()
    window.show()
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(57, 67, 69))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(57, 67, 69))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(57, 67, 69))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    sys.exit(app.exec_())
