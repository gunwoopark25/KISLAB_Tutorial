from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit

def MDIArea_add(mdi):

    for i in range(3):
        sub = QMdiSubWindow()
        sub.setWidget(QTextEdit())
        sub.setWindowTitle("Sub Window " + str(i + 1))
        mdi.addSubWindow(sub)
        sub.show()
