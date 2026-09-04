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
import train_manual, detecting_thread

trainingthread = train_manual.ThreadClass()
trainingthread.run()