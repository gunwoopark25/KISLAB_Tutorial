from PyQt5 import QtCore, QtGui, QtWidgets

class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    rectChanged = QtCore.pyqtSignal(QtCore.QRect)
    rectPoint_start = QtCore.pyqtSignal(QtCore.QPoint)
    rectPoint_end = QtCore.pyqtSignal(QtCore.QPoint)

    currentView = QtCore.pyqtSignal(float, QtCore.QSize, QtCore.QPointF)


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

    def resizeEvent(self, event):
        self.fitInView()

    def drawBox(self, data):

        boxdata = data[0]
        color = data[1]
        name = data[3]
        calibrate_x = data[4]
        calibrate_y = data[5]

        for i, boundingbox in enumerate(self.boundingboxes):
            self._scene.removeItem(boundingbox)

        for i in range(len(boxdata)):
            boundingbox = Rectangle(0,0,0,0)
            boundingbox.setRect(boxdata[i][0] + calibrate_x, boxdata[i][1] + calibrate_y, boxdata[i][2] - boxdata[i][0], boxdata[i][3] - boxdata[i][1])
            boundingbox.setPen(QtGui.QPen(QtGui.QColor(color[i][0], color[i][1], color[i][2]), 5, QtCore.Qt.SolidLine))
            boundingbox.setBrush(QtGui.QBrush(QtGui.QColor(color[i][0], color[i][1], color[i][2], 100)))
            boundingbox.setToolTip(name[i])
            self.boundingboxes.append(boundingbox)
            self._scene.addItem(boundingbox)

        self._scene.removeItem(self.rectangle)
        self._scene.addItem(self.rectangle)

    def drawCaption(self, data):

        boxdata = data[0]
        color = data[1]
        name = data[3]
        calibrate_x = data[4]
        calibrate_y = data[5]

        # for i, (caption, caption_box) in enumerate(zip(self.captions, self.caption_boxes)):
        #     self._scene.removeItem(caption)
        #     self._scene.removeItem(caption_box)

        for i, caption in enumerate(self.captions):
            self._scene.removeItem(caption)

        for i in range(len(boxdata)):
            # 이 주석은 도면 내 객체의 단순 class 표기를 위한 부분입니다
            # caption = QtWidgets.QGraphicsTextItem(name[i])
            #
            # caption.document().setDocumentMargin(0)
            # (text_width, text_height) = caption.boundingRect().width(), caption.boundingRect().height()
            # caption.setPos(boxdata[i][0] + calibrate_x, boxdata[i][1] + calibrate_y - text_height)
            #
            # captionbox = Rectangle(0,0,0,0)
            # captionbox.setRect(boxdata[i][0] + calibrate_x, boxdata[i][1] + calibrate_y - text_height, text_width, text_height)
            # captionbox.setPen(QtGui.QPen(QtGui.QColor(color[i][0], color[i][1], color[i][2]), 0, QtCore.Qt.SolidLine))
            # captionbox.setBrush(QtGui.QBrush(QtGui.QColor(color[i][0], color[i][1], color[i][2], 255)))
            #
            # self.caption_boxes.append(captionbox)
            # self._scene.addItem(captionbox)

            idx_list = [j for j, value in enumerate(name) if value == name[i]]
            num = idx_list.index(i)

            document = QtGui.QTextDocument()
            charformat = QtGui.QTextCharFormat()
            charformat.setFont(QtGui.QFont("consolas", 20))
            charformat.setForeground(QtGui.QColor(color[i][0], color[i][1], color[i][2]))
            outlinepen = QtGui.QPen(QtGui.QColor(0,0,0), 0.5)
            charformat.setTextOutline(outlinepen)

            cursor = QtGui.QTextCursor(document)
            cursor.insertText(str(num + 1), charformat)

            textitem = QtWidgets.QGraphicsTextItem()
            textitem.setDocument(document)

            (text_width, text_height) = textitem.boundingRect().width(), textitem.boundingRect().height()
            textitem.setPos((boxdata[i][0] + boxdata[i][2]) / 2 + calibrate_x - text_width / 2, (boxdata[i][1] + boxdata[i][3]) / 2 + calibrate_y - text_height / 2)


            self.captions.append(textitem)
            self._scene.addItem(textitem)

        # (text_width, text_height), baseline = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        # cv2.rectangle(image, (b[0], b[1]), (b[0] + text_width, b[1] - text_height - baseline), color,
        #               thickness=cv2.FILLED)
        # # cv2.putText(image, caption, (b[0], b[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        # cv2.putText(image, caption, (b[0], b[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

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
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

        self.fitInView()

    def setPhoto_2(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())


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

    def mouseMoveEvent(self, event):
        if self.changeRubberBand:
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            self.rectChanged.emit(self.rubberBand.geometry())
        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.changeRubberBand = False
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

        if self.isBox:
            self.rectPoint_end.emit(self.mapToScene(event.pos()).toPoint())

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

    def move_to_object(self, box):
        mid_x = int((box[0] + box[2]) / 2)
        mid_y = int((box[1] + box[3]) / 2)
        self.centerOn(mid_x, mid_y)



class Rectangle(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h):
        super(Rectangle, self).__init__(0, 0, w, h)
        self.setPen(QtGui.QPen(QtCore.Qt.red, 5, QtCore.Qt.DotLine))
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 100)))