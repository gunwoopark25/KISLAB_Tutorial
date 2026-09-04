import os
import numpy as np
from mayavi.mlab import *

# os.environ['ETS_TOOLKIT'] = 'qt4'
from pyface.qt import QtGui, QtCore
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor


def cube_faces(xmin, xmax, ymin, ymax, zmin, zmax):
    faces = []

    x,y = np.mgrid[xmin:xmax:3j,ymin:ymax:3j]
    z = np.ones(y.shape)*zmin
    faces.append((x,y,z))

    x,y = np.mgrid[xmin:xmax:3j,ymin:ymax:3j]
    z = np.ones(y.shape)*zmax
    faces.append((x,y,z))

    x,z = np.mgrid[xmin:xmax:3j,zmin:zmax:3j]
    y = np.ones(z.shape)*ymin
    faces.append((x,y,z))

    x,z = np.mgrid[xmin:xmax:3j,zmin:zmax:3j]
    y = np.ones(z.shape)*ymax
    faces.append((x,y,z))

    y,z = np.mgrid[ymin:ymax:3j,zmin:zmax:3j]
    x = np.ones(z.shape)*xmin
    faces.append((x,y,z))

    y,z = np.mgrid[ymin:ymax:3j,zmin:zmax:3j]
    x = np.ones(z.shape)*xmax
    faces.append((x,y,z))

    return faces


## create Mayavi Widget and show

class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())

    @on_trait_change('scene.activated')
    def update_plot(self):
        def mlab_plt_cube(xmin, xmax, ymin, ymax, zmin, zmax, opacity, color):
            faces = cube_faces(xmin, xmax, ymin, ymax, zmin, zmax)
            for grid in faces:
                x, y, z = grid
                mesh(x, y, z, opacity=opacity, color=color)

        # mlab_plt_cube(-500, 500, -500, 500,-100, 0, 0.3, (0, 0, 1))
        mlab_plt_cube(-100, 100, -100, 100, -100, 100, 0.5, (1, 1, 0))
        mlab_plt_cube(-200, 200, -200, 200, -1, 1, 1, (0, 0, 1))
        mlab_plt_cube(-200, 200, -1, 1, -200, 200, 1, (0, 1, 0))
        mlab_plt_cube(-1, 1, -200, 200, -200, 200, 1, (1, 0, 0))



    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True)


class Mayavi_viewer(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.visualization = Visualization()

        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control
        layout.addWidget(self.ui)
        self.ui.setParent(self)
