import sys
import os.path

from PyQt5.QtWidgets import *
from PyQt5 import uic
import urllib.request
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("test.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()

        #아이콘 및 메뉴바 설정
        self.setupUi(self)

        #각 위젯의 이름 앞에 self. 을 붙여서 지칭할 수 있음
        self.pushButton.clicked.connect(self.button_clicked)

    def button_clicked(self):
        self.label_2.setText("Clicked !")



if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()
    #프로그램 화면을 보여주는 코드
    myWindow.resize(500, 500)
    myWindow.show()
    myWindow.statusBar().showMessage('Welcome to SyDLab GUI Practice!')

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()