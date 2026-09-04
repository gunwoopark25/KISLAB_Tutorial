import time
from PyQt5.QtCore import *

class Thread2(QThread):
    data_sending = pyqtSignal(int)
    isthread = True

    def __init__(self, parent = None):
        super(Thread2,self).__init__(parent)

    def run(self):
        for i in range(100):
            if self.isthread:
                print("Thread 2: " + str(i))
                self.data_sending.emit(i)
                time.sleep(1)

            if i == 99:
                print("Thread 2: finished")
                self.isthread = True