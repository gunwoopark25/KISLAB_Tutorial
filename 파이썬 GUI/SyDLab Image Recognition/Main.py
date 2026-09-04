import sys, os, cv2
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import detectingThread
from PIL.ImageQt import ImageQt
from PIL import Image

import torch
from torch import nn
from torch.autograd import Variable
from torchvision import transforms

import random
import numpy as np
import cv2

import time

class CustomConvNet(nn.Module):
    def __init__(self):
        super(CustomConvNet, self).__init__()

        self.layer1 = self.conv_module(3, 16)
        self.layer2 = self.conv_module(16, 32)
        self.layer3 = self.conv_module(32, 64)
        self.layer4 = self.conv_module(64, 128)
        self.layer5 = self.conv_module(128, 256)
        self.gap = self.global_avg_pool(256, 2)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.layer5(out)
        out = self.gap(out)
        out = out.view(-1, 2)

        return out

    def conv_module(self, in_num, out_num):
        return nn.Sequential(
            nn.Conv2d(in_num, out_num, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(out_num),
            nn.LeakyReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))

    def global_avg_pool(self, in_num, out_num):
        return nn.Sequential(
            nn.Conv2d(in_num, out_num, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(out_num),
            nn.LeakyReLU(),
            nn.AdaptiveAvgPool2d((1, 1)))

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model_path = "helmetdata/classification_model_mask.pt"

transforms_test = transforms.Compose([transforms.Resize((128, 128)),
                                      transforms.ToTensor()])

classification_model = torch.load(model_path)
classification_model.eval()

form_class = uic.loadUiType("Main.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.arrow = cv2.imread("arrow.png", cv2.IMREAD_UNCHANGED)

        self.detectingthread = detectingThread.ThreadClass()
        self.detectingthread.signal_detected_image.connect(self.showImage)
        self.detectingthread.start()

        now = QDateTime.currentDateTime()
        date_string = now.toString('yyyy년 M월 d일')
        time_string = now.toString('AP hh:mm:ss')

        self.label.setText(date_string)
        self.label_2.setText(time_string)

        timer = QTimer(self, timeout=self.updateTime, interval=1000)
        timer.start()

    def updateTime(self):
        now = QDateTime.currentDateTime()
        date_string = now.toString('yyyy년 M월 d일')
        time_string = now.time().toString('ap hh:mm:ss')

        self.label.setText(date_string)
        self.label_2.setText(time_string)

    def showImage(self, data):
        start = time.time()
        image = data[0]

        crop_images = data[2]
        classes = data[3]
        positions = data[4]
        mask_draw = data[5]

        x_list = []
        for pos in positions:
            x = pos[0]
            x_list.append(x)
        s = np.array(x_list)
        sort_index = np.argsort(s)

        crop_images = [crop_images[i] for i in sort_index]
        classes = [classes[i] for i in sort_index]
        positions = [positions[i] for i in sort_index]
        mask_draw = [mask_draw[i] for i in sort_index]

        people_info = []
        if len(crop_images) >= 1:
            people_count = 0
            for i, (crop_img, cls, pos) in enumerate(zip(crop_images, classes, positions)):
                people_count += 1
                cv2_im = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
                crop_image = Image.fromarray(cv2_im)

                crop_image = transforms_test(crop_image)
                crop_image = np.array(crop_image)
                # print(image.shape)
                image_swap = np.expand_dims(crop_image, axis=0)
                tensor = torch.from_numpy(image_swap).type(torch.cuda.FloatTensor)

                mask_string = ""
                helmet_string = ""

                with torch.no_grad():
                    outputs = classification_model(tensor)
                    _, predicted = torch.max(outputs.data, 1)

                    if int(predicted[0]) == 0:
                        image = self.plot_helmet(pos, image, 0, "without_helmet", 3)
                        helmet_string =  "X"
                        if len(mask_draw) > 0:
                            image = self.plot_mask(mask_draw[i][0], image, mask_draw[i][1], mask_draw[i][2], mask_draw[i][3])
                        image = self.plot_num(pos, image, str(people_count), 3)
                    else:
                        image = self.plot_helmet(pos, image, 1, "with_helmet", 3)
                        helmet_string = "O"
                        if len(mask_draw) > 0:
                            image = self.plot_mask(mask_draw[i][0], image, mask_draw[i][1], mask_draw[i][2], mask_draw[i][3])
                        image = self.plot_num(pos, image, str(people_count), 3)

                    if mask_draw[i][1] == "with_mask":
                        mask_string = "O"
                    elif mask_draw[i][1] == "without_mask":
                        mask_string = "X"
                    else:
                        mask_string = "△"

                if predicted[0] == 0  or mask_draw[i][1] != 'with_mask':
                    image = self.overlay_transparent(image, self.arrow, int((pos[0] + pos[2]) / 2 - self.arrow.shape[0] / 2), int(pos[1] - self.arrow.shape[1] - 20))
                    final_judge = "불가"
                else:
                    final_judge = "통과"

                people_info.append([str(people_count), mask_string, helmet_string, final_judge])

        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(len(people_info))
        for i, info in enumerate(people_info):
            name = info[0]
            mask = info[1]
            helmet = info[2]
            result = info[3]

            table_name = QTableWidgetItem(name)
            table_mask = QTableWidgetItem(mask)
            table_helmet = QTableWidgetItem(helmet)


            table_name.setTextAlignment(Qt.AlignCenter)
            table_mask.setTextAlignment(Qt.AlignCenter)
            table_helmet.setTextAlignment(Qt.AlignCenter)

            self.tableWidget.setItem(i, 0, table_name)
            self.tableWidget.setItem(i, 1, table_mask)
            self.tableWidget.setItem(i, 2, table_helmet)

            if result == "불가":
                table_result = QLabel(result)
                table_result.setStyleSheet("background-color: rgb(255, 162, 162);font: bold 14px;")
                table_result.setAlignment(Qt.AlignCenter)
                self.tableWidget.setCellWidget(i, 3, table_result)
            else:
                table_result = QLabel(result)
                table_result.setStyleSheet("background-color: rgb(162, 255, 162);font: bold 14px;")
                table_result.setAlignment(Qt.AlignCenter)
                self.tableWidget.setCellWidget(i, 3, table_result)

        # cv2.imwrite("temp.jpg", image)
        # self.viewer = QPixmap("temp.jpg")

        height, width, bytesPerComponent = image.shape
        bytesPerLine = 3 * width
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
        QImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.viewer = QPixmap.fromImage(QImg)

        self.label_5.setPixmap(self.viewer)
        print("time :", time.time() - start)

    def plot_helmet(self, x, img, color_index, label=None, line_thickness=3):
        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
        color = [[0,0,255], [0,255,0]][color_index]
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        if label:
            tf = 2  # font thickness
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 4, thickness=tf)[0]

            c11 = (int(x[0]), int(x[3]  + 2*t_size[1] + 6))
            c3 = c11[0], c11[1] - t_size[1]
            c2 = c1[0] + t_size[0], c2[1] + 2*t_size[1] + 6

            cc1, cc2 = (int(x[0]-1.5*tl), int(x[1]-1.5*tl)), (int(x[2]+1.5*tl), int(x[3]+1.5*tl +  t_size[1]))

            cv2.rectangle(img, cc1, cc2, color, thickness=tl, lineType=cv2.LINE_AA)
            cv2.rectangle(img, (cc1[0], c3[1]), c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (cc1[0], c11[1] - 2), 0, tl / 4, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

        return img

    def plot_mask(self, x, img, label, color, line_thickness):
        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
        color = color or [random.randint(0, 255) for _ in range(3)]
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        if label:
            tf = 2  # font thickness
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 4, thickness=tf)[0]
            c3 = (int(x[0]), int(x[3]))
            c11 = (int(x[0]), int(x[3] + t_size[1] + 3))
            c2 = c1[0] + t_size[0], c2[1] + t_size[1] + 3

            cv2.rectangle(img, c3, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (c11[0], c11[1] - 2), 0, tl / 4, [225, 255, 255], thickness=tf,
                        lineType=cv2.LINE_AA)

        return img

    def plot_num(self, x, img, label, line_thickness):
        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
        color = [255,0,0]
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))

        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

        return img

    def overlay_transparent(self, background, overlay, x, y):

        background_width = background.shape[1]
        background_height = background.shape[0]


        if x >= background_width or y >= background_height:
            return background

        if x < 0 or y < 0:
            return background

        h, w = overlay.shape[0], overlay.shape[1]

        if x + w > background_width:
            w = background_width - x
            overlay = overlay[:, :w]

        if y + h > background_height:
            h = background_height - y
            overlay = overlay[:h]

        if overlay.shape[2] < 4:
            overlay = np.concatenate(
                [
                    overlay,
                    np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
                ],
                axis=2,
            )

        overlay_image = overlay[..., :3]
        mask = overlay[..., 3:] / 255.0

        background[y:y + h, x:x + w] = (1.0 - mask) * background[y:y + h, x:x + w] + mask * overlay_image

        return background

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()