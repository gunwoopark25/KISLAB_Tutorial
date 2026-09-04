from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *


class Ui_Frame(object):
  def setupUi(self, Frame):
    Frame.setObjectName("Frame")
    Frame.setStyleSheet("background-color: rgb(255, 255, 255); font: bold 'consolas' 15pt;")
    Frame.setFrameShape(QFrame.StyledPanel)
    Frame.setFrameShadow(QFrame.Raised)

    verticalLayout = QHBoxLayout(Frame)
    verticalLayout.setObjectName("verticalLayout")

    image = QLabel()
    pixmap = QPixmap("GUI/Image/about.png")
    pixmap = pixmap.scaledToWidth(50)
    image.setPixmap(pixmap)
    image.setAlignment(Qt.AlignCenter)

    str = '<p align=\"center\"><span style=\"font: bold 20px Georgia, serif ; color: black;\">Made by SyDLab</span></p>\n'\
          '<p align=\"center\"><span style=\"font: italic bold 15px Georgia, serif ; color: blue;\">-------------------------- Please contact --------------------------</span></p>\n'\
          '<p align=\"left\"><span style=\"font: bold 15px consolas ; color: black;\">Kong Minchul</span></p>\n'\
          '<p align=\"left\"><span style=\"font: bold 15px consolas ; color: black;\">System Design Lab.</span></p>\n'\
          '<p align=\"left\"><span style=\"font: bold 15px consolas ; color: black;\">Department of Naval Architecture and Ocean Engineering</span></p>\n'\
          '<p align=\"left\"><span style=\"font: bold 15px consolas ; color: black;\">Seoul National University\nRepublic of Korea</span></p>\n'\
          '<p align=\"left\"><span style=\"font: bold 15px consolas ; color: black;\">Tel. +82-2-880-8378</span></p>\n' \
          '<p align=\"left\"><span style=\"font: bold 15px consolas ; color: black;\">H.P. +82-10-4182-4673</span></p>\n' \
          '<p align=\"left\"><span style=\"font: bold 15px consolas ; color: black;\">E-mail. mckong@snu.ac.kr</span></p>\n'

    text = QLabel(str)
    line = QFrame()
    line.setFixedWidth(2)
    line.setMinimumHeight(1)
    line.setFrameShape(QFrame.VLine)
    line.setFrameShadow(QFrame.Plain)
    line.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
    line.setLineWidth(5)

    verticalLayout.addWidget(image)
    verticalLayout.addWidget(line)
    verticalLayout.addWidget(text)