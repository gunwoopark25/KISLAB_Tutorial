import sys
import os.path

from PyQt5.QtWidgets import *
from PyQt5 import uic
import urllib.request
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets

from GUI import About_Info, ConsoleOutput
from Library import QAXWidget_viewer, MDI_viewer, MATLAB_viewer, Drawing_viewer, Thread1, Thread2, Web_viewer

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("GUI_practice.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()

        self.start = True
        self.date = QDate.currentDate()

        #아이콘 및 메뉴바 설정
        self.setupUi(self)

        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip('Exit application')
        self.actionExit.triggered.connect(qApp.quit)

        self.actionAbout.triggered.connect(self.About_Program)

        self.actionAbout_PyQt.triggered.connect(self.About_PyQt)

        #상태창 시간 보여주기
        timer = QTimer(self, interval = 1000, timeout = self.showTime)
        timer.start()
        self.showTime()

        # #콘솔출력
        # Install the custom output stream
        sys.stdout = ConsoleOutput.EmittingStream(textWritten=self.normalOutputWritten)

        self.people_info = [['노명일','Professor'], ['김기수','Post Doctors'], ['이혜원','Post Doctors'], ['하지상','Ph.D. Students'], ['전도현','Ph.D. Students'], ['이성준','Ph.D. Students'], ['유동훈','Ph.D. Students'], ['김진혁','Ph.D. Students'], ['이종혁','M.Sc. Students'], ['공민철','M.Sc. Students'], ['여인창','M.Sc. Students'], ['조영민','M.Sc. Students'], ['송하민','M.Sc. Students'], ['박정호','M.Sc. Students'], ['정동근','M.Sc. Students']]
        self.setInfo()

        # 비트코인 시세 가져오기
        self.bitcoinViewer = QAXWidget_viewer.BitCoin_thread()
        self.bitcoinViewer.data_sending.connect(self.showBitcoin)
        self.bitcoinViewer.start()

        # 텍스트 바꾸기 예제
        for i in [10,12,14,16,18,20]:
            self.comboBox.addItem(str(i) + ' px')

        self.fontComboBox.currentFontChanged.connect(self.setlabelFont)
        self.comboBox.currentIndexChanged.connect(self.setlabelFont)

        # MDI 뷰어
        MDI_viewer.MDIArea_add(self.mdiArea)
        self.mdiArea.tileSubWindows()

        # 그림판 뷰어
        self.drawingViewer = Drawing_viewer.DrawingViewer()
        self.verticalLayout_61.addWidget(self.drawingViewer)

        # 매트랩 뷰어
        self.matlabViewer = MATLAB_viewer.MATLABViwer()
        self.verticalLayout_66.addWidget(self.matlabViewer)

        # # OpenGL 뷰어
        # self.openglViewer = OpenGL_viewer.OpenGLViewer()
        # self.verticalLayout_67.addWidget(self.openglViewer)
        #
        # # Mayavi 뷰어
        # self.mayavi_widget = Mayavi_viewer.Mayavi_viewer()
        # self.verticalLayout_68.addWidget(self.mayavi_widget)

        #Web 뷰어
        self.webViewer = Web_viewer.webViewer()
        self.verticalLayout_67.addWidget(self.webViewer)

        # 쓰레드 연습
        self.pushButton_22.clicked.connect(self.thread1Start)
        self.pushButton_24.clicked.connect(self.thread2Start)

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quit?',
                                     'Are you sure you want to quit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not type(event) == bool:
                event.accept()
            else:
                sys.exit()
        else:
            if not type(event) == bool:
                event.ignore()

    def thread1Start(self):
        self.thread1 = Thread1.Thread1()

        def threadvisualize(tick):
            self.label_74.setText(str(tick))
        def threadreset():
            self.thread1.isthread = False
            self.label_74.setText(str(0))

        self.thread1.data_sending.connect(threadvisualize)
        self.thread1.start()

        self.pushButton_23.clicked.connect(threadreset)

    def thread2Start(self):
        self.thread2 = Thread2.Thread2()

        def threadvisualize(tick):
            self.label_75.setText(str(tick))
        def threadreset():
            self.thread2.isthread = False
            self.label_75.setText(str(0))

        self.thread2.data_sending.connect(threadvisualize)
        self.thread2.start()

        self.pushButton_25.clicked.connect(threadreset)

    def normalOutputWritten(self, text):#print 출력 동기화
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.textEdit_2.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit_2.setTextCursor(cursor)
        self.textEdit_2.ensureCursorVisible()

    def About_PyQt(self):
        url = QtCore.QUrl('https://en.wikipedia.org/wiki/PyQt')
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')

    def About_Program(self):
        ui = About_Info.Ui_Frame()
        Frame = QtWidgets.QFrame()
        ui.setupUi(Frame)
        self.aboutui = Frame
        self.aboutui.show()
        self.aboutui.setWindowTitle("About")
        self.aboutui.setWindowIcon(QIcon('GUI/Image/about.png'))

    def showTime(self):
        datetime = QDateTime.currentDateTime()
        self.statusBar().showMessage(datetime.toString('yyyy년 MM월 dd일 hh:mm'))

    def setInfo(self):
        # 리스트 위젯
        for people in self.people_info:
            name = people[0]
            position = people[1]

            self.listWidget.addItem(position + " : " + name)

        def listItemClicked():#아이템 클릭 시 텍스트 변경
            self.label_64.setText(self.listWidget.currentItem().text())
        self.listWidget.clicked.connect(listItemClicked)

        # 트리 위젯
        for pos in ['Professor', 'Post Doctors', 'Ph.D. Students', 'M.Sc. Students']:
            itemTop1 = QTreeWidgetItem(self.treeWidget)
            itemTop1.setText(0, pos)

            for people in self.people_info:
                name = people[0]
                position = people[1]

                if pos == position:
                    itemTop2 = QTreeWidgetItem(itemTop1)
                    itemTop2.setText(0, name)
        self.treeWidget.expandAll()

        def treeItemClicked(item, column):#아이템 클릭 시 텍스트 변경
            self.label_65.setText(item.text(column))
        self.treeWidget.itemClicked.connect(treeItemClicked)

        # 테이블 위젯
        self.tableWidget.setRowCount(len(self.people_info))
        self.tableWidget.setColumnCount(2)
        for i, people in enumerate(self.people_info):
            name = people[0]
            position = people[1]
            self.tableWidget.setItem(i, 0, QTableWidgetItem(position))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(name))

        def tableItemClicked(item):#아이템 클릭 시 텍스트 변경
            self.label_66.setText(item.text())
        self.tableWidget.itemClicked.connect(tableItemClicked)


    def setlabelFont(self):
        font_name = self.fontComboBox.currentText()
        font_size = int(self.comboBox.currentText().split(' ')[0])
        self.label_50.setFont(QFont(font_name, font_size))

    def showBitcoin(self, data):
        self.label_63.setText(data[0])

        text = data[1].split(' ')[0]
        text = text.replace(',', '')

        if float(text) < 0:
            self.label_62.setStyleSheet("QLabel{color: red;}")
        elif float(text) == 0:
            self.label_62.setStyleSheet("QLabel{color: grey;}")
        else:
            self.label_62.setStyleSheet("QLabel{color: green;}")

        self.label_62.setText(data[1])



if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()
    #프로그램 화면을 보여주는 코드
    myWindow.resize(1600, 1000)
    # myWindow.setMinimumSize(QSize(1600, 1000))
    myWindow.show()
    myWindow.statusBar().showMessage('Welcome to SyDLab GUI Practice!')

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    sys.exit(app.exec_())