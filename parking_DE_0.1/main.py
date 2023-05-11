import torch  # will be used to load the yolo model and make the detection
# for seeing images
# from matplotlib import pyplot as plt
import numpy as np  # for array transformation
import cv2  # for access the webcam and render feeds
import os
from time import time
import cvzone


def load_model():
    """
    Loads Yolo5 model from pytorch hub.
    :return: Trained Pytorch model.
    """
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp6/weights/best.pt',
                           force_reload=True)
    return model


class ObjectDetection:
    """
    class object to detect parking places
    """

    def __init__(self, capture_index):
        """

        """
        print("def __init__ first")
        self.capture_index = capture_index
        self.model = load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        print("def __init__ last")

    def get_video_capture(self):
        """
        Creates a new video streaming object to extract video frame by frame to make prediction on.
        :return: opencv2 video capture object
        """
        print("def get_video_capture")
        return cv2.VideoCapture(self.capture_index)

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using the model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        print("def score_frame_first")
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        print("def score_frame_last")
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        print("def class_to_label")
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        print("def plot_boxes_first")
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        carCounter_empty = 0
        carCounter_full = 0
        lot_number = 0
        print("def plot_boxes_before_forLoop")
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.3:
                x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape),\
                                 int(row[2] * x_shape), int(
                    row[3] * y_shape)

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
                                (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, empty,
                                1)
                    cv2.putText(frame, str(lot_number), (x2, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, full, 1)
                    carCounter_empty += 1
                    lot_number += 1

            cvzone.putTextRect(frame, "Empty:", (10, 60), scale=1,
                               thickness=1, offset=0, colorR=(0, 255, 0,))

            cvzone.putTextRect(frame, str(carCounter_empty), (70, 60), scale=1,
                               thickness=1, offset=0, colorR=(0, 255, 0,))

            cvzone.putTextRect(frame, "Full:", (10, 40), scale=1,
                               thickness=1, offset=0, colorR=(0, 0, 255,))

            cvzone.putTextRect(frame, str(carCounter_full), (50, 40), scale=1,
                               thickness=1, offset=0, colorR=(0, 0, 255,))
        print("def plot_boxes_after_forLoop")

        return frame

    def __call__(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """
        print("def __call__before_whileLoop")
        cap = self.get_video_capture()

        assert cap.isOpened()

        while True:

            start_time = time()

            ret, frame = cap.read()
            assert ret

            results = self.score_frame(frame)
            frame = self.plot_boxes(results, frame)

            end_time = time()
            fps = 1 / np.round(end_time - start_time, 2)
            # print(f"Frames Per Second : {fps}")

            cv2.putText(frame, f'FPS: {int(fps)}', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            cv2.imshow('Parking DE', frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()


# Create a new object and execute.
detector = ObjectDetection(capture_index="carPark.mp4")
detector()
