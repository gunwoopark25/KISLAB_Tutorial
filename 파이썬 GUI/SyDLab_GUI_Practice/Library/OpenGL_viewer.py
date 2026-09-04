from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import itertools
from PyQt5.QtWidgets import QOpenGLWidget

class OpenGLViewer(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(OpenGLViewer, self).__init__(parent)

        self.opts['distance'] = 3

        vertexes = np.array(list(itertools.product(range(2),repeat=3)))

        faces = []

        for i in range(2):
            temp = np.where(vertexes==i)
            for j in range(3):
                temp2 = temp[0][np.where(temp[1]==j)]
                for k in range(2):
                    faces.append([temp2[0],temp2[1+k],temp2[3]])

        faces = np.array(faces)

        colors = np.array([[1,0,0,1] for i in range(12)])


        cube = gl.GLMeshItem(vertexes=vertexes, faces=faces, faceColors=colors,
                             drawEdges=True, edgeColor=(0, 1, 1, 1))

        self.addItem(cube)


# if __name__ == '__main__':
#     import sys
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()