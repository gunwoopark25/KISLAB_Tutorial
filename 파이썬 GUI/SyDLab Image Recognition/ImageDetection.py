import sys
import os.path
from pathlib import Path

import cv2
from PyQt5.QtWidgets import *
from PyQt5 import uic
import urllib.request
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from GUI import color, ConsoleOutput
import training_thread, detecting_thread

form_class = uic.loadUiType("GUI.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        logo = QLabel()
        logo.setStyleSheet("margin-bottom:5px")
        pixmap = QPixmap("Icon/sydlab_logo.png")
        logo.setPixmap(pixmap)
        self.tabWidget.setCornerWidget(logo, QtCore.Qt.TopRightCorner)

        timer = QTimer(self, interval=5000, timeout=self.showTime)
        timer.start()
        self.showTime()

        sys.stdout = ConsoleOutput.EmittingStream(textWritten=self.normalOutputWritten)

        self.toolButton.clicked.connect(self.loadImagePath)
        self.toolButton_2.clicked.connect(self.loadLabeledImagePath)
        self.toolButton_3.clicked.connect(self.loadModel)
        self.toolButton_4.clicked.connect(self.loadVideo)

        self.boxes = []
        self.imageViewer = PhotoViewer(self)
        self.verticalLayout_6.addWidget(self.imageViewer)
        self.imageViewer.boxClicked.connect(self.boxClicked)
        self.imageViewer.notClicked.connect(self.notClicked)

        hbox = QHBoxLayout()
        radiobutton = QRadioButton("Class 1")
        radiobutton.setStyleSheet('font: 10pt "Arial Rounded MT Bold"')
        radiobutton.setFixedWidth(100)
        radiobutton.setChecked(True)
        radiobutton.clicked.connect(self.changeClass)
        hbox.addWidget(radiobutton)
        hbox.addWidget(QLineEdit())
        self.verticalLayout_11.addLayout(hbox)

        self.class_group = []
        self.class_group.append(radiobutton)
        self.layout_group = []
        self.layout_group.append(hbox)
        self.pushButton_2.setEnabled(False)

        self.pushButton.clicked.connect(self.addClass)
        self.pushButton_2.clicked.connect(self.deleteClass)

        self.pushButton_4.clicked.connect(self.pageForward)
        self.pushButton_8.clicked.connect(self.pageBackward)
        self.pushButton_4.setEnabled(False)
        self.pushButton_8.setEnabled(False)

        self.pushButton_3.clicked.connect(self.drawMode)
        self.pushButton_5.clicked.connect(self.drawBox)
        self.pushButton_6.clicked.connect(self.deleteBox)
        self.pushButton_5.hide()
        self.pushButton_6.hide()

        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.setWindowTitle("Error")

        self.pushButton_7.clicked.connect(self.startTraining)
        self.pushButton_11.clicked.connect(self.startDetecting)

        self.radioButton.clicked.connect(self.videoMode)
        self.radioButton_2.clicked.connect(self.webcamMode)
        self.video_source = str(0)
        self.widget_3.hide()

    def videoMode(self):
        self.widget_3.show()
    def webcamMode(self):
        self.widget_3.hide()
        self.video_source = str(0)

    def loadVideo(self):
        fname = QFileDialog.getOpenFileName(self, 'Open your video file', '', "Videos (*.mp4);; All Files(*)")
        self.label_17.setText(fname[0])

        dirname = os.path.dirname(__file__)
        self.video_source = os.path.relpath(self.label_17.text(), dirname)

    def loadModel(self):
        fname = QFileDialog.getOpenFileName(self, 'Open your trained model', '',"Model (*.pt);; All Files(*)")
        self.label_12.setText(fname[0])

    def startDetecting(self):
        if self.label_12 != None and self.label_12 != '':
            dirname = os.path.dirname(__file__)
            relpath = os.path.relpath(self.label_12.text(), dirname)

            source = self.video_source

            self.detectingthread = detecting_thread.ThreadClass(source, relpath)
            self.detectingthread.signal_detected_image.connect(self.showImage)
            self.detectingthread.start()

    def showImage(self, data):
        image = data[0]
        text = data[1]

        # print(text)

        height, width, bytesPerComponent = image.shape
        bytesPerLine = 3 * width
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
        QImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.viewer = QPixmap.fromImage(QImg)

        self.label_5.setPixmap(self.viewer)

    def startTraining(self):
        if self.label_8 != None and self.label_8 != '':
            temp_class = []
            for i, file in enumerate(os.listdir(self.labeled_label_folder_path)):
                for line in open(self.labeled_label_folder_path + "/" + file, 'r'):
                    class_num = int(line.split(" ")[0])
                    temp_class.append(class_num)

            num_classes = max(temp_class) + 1
            classed_name = []
            for lineEdit in self.class_name:
                classed_name.append(lineEdit.text())

            self.make_yaml(num_classes, classed_name)

            YOLOModel = self.comboBox_4.currentText()
            ImageSize = self.comboBox.currentText()
            Epochs = str(self.spinBox.value())
            BatchSize = self.comboBox_2.currentText()
            Yaml = self.yaml_name
            Name = self.lineEdit.text()

            # print(YOLOModel, ImageSize, Epochs, BatchSize, Yaml, Name)
            self.trainingthread = training_thread.ThreadClass(YOLOModel, ImageSize, Epochs, BatchSize, Yaml, Name)
            self.trainingthread.isthread = True
            self.trainingthread.signal_train_progressbar.connect(self.progressbar)
            def quit_thread():
                self.trainingthread.isthread = False

            self.trainingthread.start()

    def progressbar(self, val):
        self.progressBar.setValue(val)

    def pageForward(self):
        current_page = int(self.label.text())

        if current_page != 1:
            self.label.setText(" " + str(current_page - 1))
            self.goImage2(current_page-2)
        else:
            pass

    def pageBackward(self):
        current_page = int(self.label.text()[1:])
        last_page = int(self.label_2.text().split(" ")[2])

        if current_page != last_page:
            self.label.setText(" " + str(current_page + 1))
            self.goImage2(current_page)
        else:
            pass

    def pageEnd(self):
        current_page = int(self.label.text()[1:])
        last_page = int(self.label_2.text().split(" ")[2])

        self.pushButton_4.setEnabled(True)
        self.pushButton_8.setEnabled(True)

        if current_page != 1:
            pass
        else:
            self.pushButton_4.setEnabled(False)

        if current_page != last_page:
            pass
        else:
            self.pushButton_8.setEnabled(False)

    def loadImagePath(self):
        self.image_folder_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.label_6.setText(self.image_folder_path)

        if self.image_folder_path != None and self.image_folder_path != '':
            self.fileModel = QFileSystemModel()
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Files)

            self.treeView.setModel(self.fileModel)
            self.treeView.setRootIndex(self.fileModel.setRootPath(self.image_folder_path))
            self.treeView.clicked.connect(self.goImage)

            count = 0
            self.image_index = []
            for i, file in enumerate(os.listdir(self.image_folder_path)):
                if file.endswith(".jpg") or file.endswith(".png"):
                    count += 1
                    self.image_index.append(i)
            self.label_2.setText(" / " + str(count) + " ")

            self.label_folder_path = "/".join(self.image_folder_path.split("/")[:-1]) + "/" + "labels"
            # print(self.label_folder_path)
            if not os.path.isdir(self.label_folder_path):
                reply = QMessageBox.question(self, 'Make folder?',
                                             '라벨 데이터가 없습니다. 폴더를 새로 만드시겠습니까?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    os.mkdir(self.label_folder_path)
                else:
                    pass
            else:
                try:
                    temp_class = []
                    for i, file in enumerate(os.listdir(self.label_folder_path)):
                        for line in open(self.label_folder_path + "/" + file, 'r'):
                            class_num = int(line.split(" ")[0])
                            temp_class.append(class_num)

                    num_classes = max(temp_class) + 1

                    if num_classes == len(self.class_group):
                        pass
                    elif num_classes > len(self.class_group):
                        for i in range(num_classes - len(self.class_group)):
                            self.addClass()
                    else:
                        for i in range(len(self.class_group - num_classes)):
                            self.deleteClass()
                except:
                    print("Wrong Label File!")

    def loadLabeledImagePath(self):
        self.labeled_image_folder_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.label_8.setText(self.labeled_image_folder_path)

        if self.labeled_image_folder_path != None and self.labeled_image_folder_path != '':
            self.labeled_label_folder_path = "/".join(self.labeled_image_folder_path.split("/")[:-1]) + "/" + "labels"

            if not os.path.isdir(self.labeled_label_folder_path):
                self.error_dialog.showMessage('Wrong Label Data! Please check your labeled data')
            else:
                temp_class = []
                for i, file in enumerate(os.listdir(self.labeled_label_folder_path)):
                    for line in open(self.labeled_label_folder_path + "/" + file, 'r'):
                        class_num = int(line.split(" ")[0])
                        temp_class.append(class_num)

                num_classes = max(temp_class) + 1
                self.deleteItemsOfLayout(self.verticalLayout_19)
                self.class_name = []
                for i in range(num_classes):
                    hbox = QHBoxLayout()
                    label = QLabel("Class " + str(i + 1) + " : ")
                    label.setStyleSheet('font: 10pt "Arial Rounded MT Bold"')
                    label.setFixedWidth(100)

                    lineEdit = QLineEdit()
                    self.class_name.append(lineEdit)

                    hbox.addWidget(label)
                    hbox.addWidget(lineEdit)
                    self.verticalLayout_19.addLayout(hbox)


    def goImage(self, index):
        image_path = self.image_folder_path + '/' + index.data()
        self.delBox()
        self.boxes = []

        if image_path.endswith(".jpg") or image_path.endswith(".png"):
            self.image_path = image_path
            pixmap = QPixmap(image_path)
            self.imageViewer.setPhoto(pixmap)
            self.label.setText(" " + str(self.image_index.index(index.row())+1))

            self.pageEnd()
            self.makeLabel(image_path)

    def goImage2(self, index):
        self.delBox()
        self.boxes = []

        for i, file in enumerate(os.listdir(self.image_folder_path)):
                if i == self.image_index[index]:
                    image_path = self.image_folder_path + "/" + file
                    self.image_path = image_path
                    pixmap = QPixmap(image_path)
                    self.imageViewer.setPhoto(pixmap)
                    self.label.setText(" " + str(self.image_index.index(i) + 1))

                    self.pageEnd()
                    self.makeLabel(image_path)
                    break

    def makeLabel(self, image_path):
        file_name = image_path.split("/")[-1].split(".")[0]
        label_path = self.label_folder_path
        label_file_name = label_path + "/" + file_name + ".txt"

        if not os.path.isfile(label_file_name):
            f = open(label_file_name, 'w')
            f.close()

        else:
            box_data = []
            for line in open(label_file_name, 'r'):
                line = line.rstrip('\n')
                box_data.append(line.split(" "))

            raw_image = cv2.imread(image_path)

            for data in box_data:
                class_num = int(data[0])
                x_center = float(data[1])
                y_center = float(data[2])
                width = float(data[3])
                height = float(data[4])

                image_width = raw_image.shape[1]
                image_height = raw_image.shape[0]

                LT, RB = (((int((x_center-width/2)*image_width),int((y_center-height/2)*image_height))), ((int((x_center+width/2)*image_width),int((y_center+height/2)*image_height))))
                # box_color = tuple(color.label_color(class_num))
                # cv2.rectangle(draw, LT, RB, box_color, thickness=1, lineType=cv2.LINE_AA)

                rectangle = Rectangle(0, 0, 0, 0)
                rectangle.class_index = class_num
                self.boxes.append(rectangle)

                box_color = color.label_color(rectangle.class_index)
                rectangle.setPen(QtGui.QPen(QtGui.QColor(box_color[0], box_color[1], box_color[2], 255), 1, QtCore.Qt.SolidLine))
                rectangle.setBrush(QtGui.QBrush(QtGui.QColor(box_color[0], box_color[1], box_color[2], 100)))

                self.imageViewer._scene.addItem(rectangle)
                rectangle.setRect(LT[0], LT[1], RB[0] - LT[0], RB[1] - LT[1])

    def drawMode(self):
        if self.imageViewer.isBox:
            self.imageViewer.changeRubberBand = False
            self.imageViewer.isBox = False
            self.pushButton_3.setText("Draw Box")
            self.pushButton_3.setStyleSheet('QPushButton{border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold"; padding: 1px}\nQPushButton:hover { background-color : rgb(240,240,240); border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold";padding: 1px}\nQPushButton:pressed { background-color : black; border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold"; color: white;padding: 1px}')
            self.imageViewer.rubberBand.hide()
            self.pushButton_5.hide()
        else:
            self.imageViewer.changeRubberBand = True
            self.imageViewer.isBox = True

            self.pushButton_3.setText("Cancel")
            self.pushButton_3.setStyleSheet(
                """QPushButton{background-color : rgb(255,200,200); border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold";padding: 1px}\nQPushButton:hover {background-color : rgb(255,150,150);; border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold";padding: 1px}\nQPushButton:pressed {background-color : rgb(255,0,0);; border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold"; color: white;padding: 1px}""")
            self.pushButton_5.show()

            self.imageViewer.rubberBand.setGeometry(QtCore.QRect(QPoint(-1,-1), QtCore.QSize()))

    def drawBox(self):###########
        start = self.imageViewer.mapToScene(self.imageViewer.rubberBand.pos())
        end = self.imageViewer.rectPoint_end_save

        if start.x() >= 0 and start.x() < self.imageViewer._photo.pixmap().width():
            if end.y() >= 0 and end.y() < self.imageViewer._photo.pixmap().height():
                rectangle = Rectangle(0,0,0,0)
                self.boxes.append(rectangle)
                self.imageViewer._scene.addItem(rectangle)
                rectangle.setRect(start.x(),start.y(), end.x()-start.x(), end.y()-start.y())

        self.imageViewer.changeRubberBand = False
        self.imageViewer.isBox = False
        self.pushButton_3.setText("Draw Box")
        self.pushButton_3.setStyleSheet(
            'QPushButton{border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold"; padding: 1px}\nQPushButton:hover { background-color : rgb(240,240,240); border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold";padding: 1px}\nQPushButton:pressed { background-color : black; border: 1px solid black; border-radius: 5px; font: 11pt "Arial Rounded MT Bold"; color: white;padding: 1px}')
        self.imageViewer.rubberBand.hide()
        self.pushButton_5.hide()

        self.saveBox()

    def notClicked(self):
        self.pushButton_6.hide()

    def boxClicked(self, item):
        for i, rad_bt in enumerate(self.class_group):
            if i == item.class_index:
                rad_bt.setChecked(True)
            else:
                rad_bt.setChecked(False)

        for _item in self.boxes:
            box_color = color.label_color(_item.class_index)
            if item == _item:
                self.selected_box = _item
                self.pushButton_6.show()
                _item.setPen(QtGui.QPen(QtGui.QColor(box_color[0], box_color[1], box_color[2], 255), 1, QtCore.Qt.SolidLine))
                _item.setBrush(QtGui.QBrush(QtGui.QColor(box_color[0], box_color[1], box_color[2], 100)))
            else:
                _item.setPen(QtGui.QPen(QtGui.QColor(box_color[0], box_color[1], box_color[2], 255), 1, QtCore.Qt.DotLine))
                _item.setBrush(QtGui.QBrush(QtGui.QColor(box_color[0], box_color[1], box_color[2], 50)))

    def changeClass(self):
        if not len(self.boxes) == 0:
            for i, rd_bt in enumerate(self.class_group):
                if rd_bt.isChecked():
                    self.selected_box.class_index = i
                    box_color = color.label_color(self.selected_box.class_index)
                    self.selected_box.setPen(QtGui.QPen(QtGui.QColor(box_color[0], box_color[1], box_color[2], 255), 1, QtCore.Qt.SolidLine))
                    self.selected_box.setBrush(QtGui.QBrush(QtGui.QColor(box_color[0], box_color[1], box_color[2], 100)))

                    self.saveBox()

    def deleteBox(self):
        for i, box in enumerate(self.boxes):
            if box == self.selected_box:
                del self.boxes[i]

        self.imageViewer._scene.removeItem(self.selected_box)
        self.pushButton_6.hide()

        self.saveBox()

    def saveBox(self):
        file_name = self.image_path.split("/")[-1].split(".")[0]
        label_path = self.label_folder_path
        label_file_name = label_path + "/" + file_name + ".txt"

        raw_image = cv2.imread(self.image_path)

        if len(self.boxes) != 0:
            line = []
            for box in self.boxes:
                x = box.rect().x()
                y = box.rect().y()
                width = box.rect().width()
                height = box.rect().height()
                class_num = box.class_index

                norm_x_center = (x + width / 2) / raw_image.shape[1]
                norm_y_center = (y + height / 2) / raw_image.shape[0]
                norm_width = width / raw_image.shape[1]
                norm_height = height / raw_image.shape[0]

                line.append(" ".join(
                    [str(class_num), str(norm_x_center), str(norm_y_center), str(norm_width), str(norm_height)]) + "\n")

            f = open(label_file_name, 'w')
            for i, l in enumerate(line):
                if i != len(line) - 1:
                    f.write(l)
                else:
                    f.write(l.rstrip("\n"))
            f.close()

        else:
            f = open(label_file_name, 'w')
            f.close()

    def addClass(self):
        hbox = QHBoxLayout()
        radiobutton = QRadioButton("Class " + str(self.verticalLayout_11.count()+1))
        radiobutton.setStyleSheet('font: 10pt "Arial Rounded MT Bold"')
        radiobutton.setFixedWidth(100)
        radiobutton.clicked.connect(self.changeClass)
        hbox.addWidget(radiobutton)
        hbox.addWidget(QLineEdit())
        self.verticalLayout_11.addLayout(hbox)

        self.class_group.append(radiobutton)
        self.layout_group.append(hbox)
        self.pushButton_2.setEnabled(True)

    def deleteClass(self):
        if self.verticalLayout_11.count() - 1 != 0:
            target_layout = self.layout_group[self.verticalLayout_11.count() - 1]
            self.deleteItemsOfLayout(target_layout)
            self.verticalLayout_11.removeItem(target_layout)

            self.class_group.pop(-1)
            self.layout_group.pop(-1)

        if self.verticalLayout_11.count() - 1 == 0:
            self.pushButton_2.setEnabled(False)

    def deleteItemsOfLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())

    def make_yaml(self, num_classes, class_names):
        yaml_name = self.labeled_image_folder_path.split("/")[-2] + ".yaml"

        dirname = os.path.dirname(__file__)
        relpath = os.path.relpath(self.labeled_image_folder_path, dirname)

        yaml_name = yaml_name.split('.')[0] + "/" + yaml_name
        f = open(yaml_name, 'w')
        f.write("train: " + relpath + "/\n")
        f.write("val: " + relpath + "/\n")
        f.write("nc: " + str(num_classes) + "\n")
        f.write("names: " + str(class_names))
        f.close()

        self.yaml_name = yaml_name

    def showTime(self):
        datetime = QDateTime.currentDateTime()
        self.statusBar().showMessage(datetime.toString('yyyy년 MM월 dd일 hh:mm'))

    def delBox(self):
        for i, boundingbox in enumerate(self.boxes):
            self.imageViewer._scene.removeItem(boundingbox)

    def normalOutputWritten(self, text):#print 출력 동기화
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        if self.tabWidget.currentIndex() == 1:
            cursor = self.textEdit.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            self.textEdit.setTextCursor(cursor)
            self.textEdit.ensureCursorVisible()
        if self.tabWidget.currentIndex() == 2:
            cursor = self.textEdit_2.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            self.textEdit_2.setTextCursor(cursor)
            self.textEdit_2.ensureCursorVisible()

#######################################################################################################
class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    rectChanged = QtCore.pyqtSignal(QtCore.QRect)
    rectPoint_start = QtCore.pyqtSignal(QtCore.QPoint)
    rectPoint_end = QtCore.pyqtSignal(QtCore.QPoint)

    currentView = QtCore.pyqtSignal(float, QtCore.QSize, QtCore.QPointF)

    boxClicked = QtCore.pyqtSignal(QGraphicsRectItem)
    notClicked = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene()
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(240, 240, 240)))
        # self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding))
        # self.setFrameShape(QtWidgets.QFrame.NoFrame)


        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.setMouseTracking(True)
        self.origin = QtCore.QPoint()
        self.changeRubberBand = False
        self.isBox = False

        self.boundingboxes = []
        self.captions = []
        self.captions2 = []
        self.caption_boxes = []

        self.rectangle = Rectangle(0, 0, 0, 0)
        self.rectangle.class_index = 9999

        self.rectPoint_end_save = QPointF(0,0)

        self.h_line = QtCore.QLineF(0, 0, 1000, 0)
        self.v_line = QtCore.QLineF(0, 0, 0, 1000)
        penlnk = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.SolidLine)
        self.lnk1 = QGraphicsLineItem(self.h_line)
        self.lnk1.setPen(penlnk)
        self.lnk2 = QGraphicsLineItem(self.v_line)
        self.lnk2.setPen(penlnk)
        self._scene.addItem(self.lnk1)
        self._scene.addItem(self.lnk2)


    def resizeEvent(self, event):
        self.fitInView()

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            # self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

        self.fitInView()


    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

            self.currentView.emit(self._zoom, self.size(), self.mapToScene(self.viewport().rect().center()))

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

        if self.isBox:
            if self.hasPhoto():
                if self.mapToScene(event.pos()).toPoint().x() >= 0 and self.mapToScene(
                        event.pos()).toPoint().x() < self._photo.pixmap().width():
                    if self.mapToScene(event.pos()).toPoint().y() >= 0 and self.mapToScene(
                        event.pos()).toPoint().y() < self._photo.pixmap().height():

                        self.origin = event.pos()
                        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
                        self.rectChanged.emit(self.rubberBand.geometry())
                        self.rubberBand.show()
                        self.changeRubberBand = True
                        QtWidgets.QGraphicsView.mousePressEvent(self, event)

                        self.rectPoint_start.emit(self.mapToScene(event.pos()).toPoint())
        # print(self.mapToScene(self.viewport().rect().center()))
        # print(self.size())
        self.currentView.emit(self._zoom, self.size(), self.mapToScene(self.viewport().rect().center()))

        item = self.itemAt(event.pos())
        try:
            class_index = item.class_index
            self.boxClicked.emit(item)
        except:
            self.notClicked.emit()

    def mouseMoveEvent(self, event):
        if self.hasPhoto():
            if self.mapToScene(event.pos()).toPoint().x() >= 0 and self.mapToScene(event.pos()).toPoint().x() < self._photo.pixmap().width():
                if self.mapToScene(event.pos()).toPoint().y() >= 0 and self.mapToScene(event.pos()).toPoint().y() < self._photo.pixmap().height():
                    if self.changeRubberBand:
                        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                        self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
                        self.rectChanged.emit(self.rubberBand.geometry())

                    pos = QtCore.QPointF(0, self.mapToScene(event.pos()).toPoint().y())
                    self.h_line.setP1(pos)
                    pos = QtCore.QPointF(self._photo.pixmap().width(), self.mapToScene(event.pos()).toPoint().y())
                    self.h_line.setP2(pos)
                    self.lnk1.setLine(self.h_line)

                    pos = QtCore.QPointF(self.mapToScene(event.pos()).toPoint().x(), 0)
                    self.v_line.setP1(pos)
                    pos = QtCore.QPointF(self.mapToScene(event.pos()).toPoint().x(), self._photo.pixmap().height())
                    self.v_line.setP2(pos)
                    self.lnk2.setLine(self.v_line)

        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.changeRubberBand = False
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

        if self.isBox:
            self.rectPoint_end.emit(self.mapToScene(event.pos()).toPoint())
            self.rectPoint_end_save = self.mapToScene(event.pos()).toPoint()

        self.currentView.emit(self._zoom, self.size(), self.mapToScene(self.viewport().rect().center()))

    def get_scroll_state(self):
        """
        Returns a tuple of scene extents percentages.
        """
        centerPoint = self.mapToScene(self.viewport().width() / 2,
                                      self.viewport().height() / 2)
        sceneRect = self.sceneRect()
        centerWidth = centerPoint.x() - sceneRect.left()
        centerHeight = centerPoint.y() - sceneRect.top()
        sceneWidth = sceneRect.width()
        sceneHeight = sceneRect.height()

        sceneWidthPercent = centerWidth / sceneWidth if sceneWidth != 0 else 0
        sceneHeightPercent = centerHeight / sceneHeight if sceneHeight != 0 else 0
        return sceneWidthPercent, sceneHeightPercent

    def set_scroll_state(self, scroll_state):
        sceneWidthPercent, sceneHeightPercent = scroll_state
        x = (sceneWidthPercent * self.sceneRect().width() +
             self.sceneRect().left())
        y = (sceneHeightPercent * self.sceneRect().height() +
             self.sceneRect().top())
        self.centerOn(x, y)


class Rectangle(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h):
        super(Rectangle, self).__init__(0, 0, w, h)
        self.class_index = 0
        box_color = color.label_color(self.class_index)

        self.setPen(QtGui.QPen(QtGui.QColor(box_color[0], box_color[1], box_color[2], 255), 1, QtCore.Qt.DotLine))
        self.setBrush(QtGui.QBrush(QtGui.QColor(box_color[0], box_color[1], box_color[2], 50)))

    def hoverEnterEvent(self, event):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.PointingHandCursor)

    def hoverLeaveEvent(self, event):
        QtWidgets.QApplication.restoreOverrideCursor()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    myWindow.statusBar().showMessage('Welcome to SyDLab Image Detection Program!')
    sys.exit(app.exec_())

