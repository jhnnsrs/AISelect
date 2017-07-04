import numpy as np
import cv2

from matplotlib.path import Path
import matplotlib.patches as patches
from elements import Roi
from settings import Global


class LineBuilder(object):
    lock = None  # only one line can be build at a time

    def __init__(self, ax, fig, img):

        self.fig = fig
        self.img = img

        self.locked = False  # is set by other

        self.roicount = 0
        self.roi = None

        # TODO: this should be outside
        self.ax = ax
        self.ax.set_xlim([0, img.shape[0]])
        self.ax.set_ylim([0, img.shape[1]])

        self.imageCallback = None
        self.roiCallback = None

        self.line = None
        self.channels = img.shape[2]

        self.lastvector = np.array([0, 0])
        self.lastdot = np.array([0, 0])
        self.dotthreshold = 3
        self.vectorthreshold = 3

        self.cid = fig.canvas.mpl_connect('button_press_event', self.on_pressevent)
        self.cidrelease = fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid2 = fig.canvas.mpl_connect('key_press_event', self.on_keyevent)

    def setImageCallback(self, callback):
        self.imageCallback = callback

    def setRoiCallback(self, callback):
        self.roiCallback = callback

    def on_pressevent(self, event):
        print("PRESSEVENT")
        if self.locked: return
        if event.inaxes != self.ax: return
        if not self.line: self.line, = self.ax.plot([event.xdata, event.ydata])  # first generate line
        LineBuilder.lock = self

        self.roi = Roi(self.roicount)
        self.roicount += 1
        self.roi.setNewBoxCallback(self.drawBox)
        self.roi.setImageCallback(self.imageCallback)
        self.roi.setRoiCallback(self.roiCallback)

    def drawBox(self, box):

        verts, width = box
        vertices = verts + [[0, 0]]  # dummy
        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.CLOSEPOLY,
                 ]

        path = Path(vertices, codes)

        patch = patches.PathPatch(path, facecolor='orange', lw=1)
        patch = self.ax.add_patch(patch)
        self.roi.patcheslink.append(patch)
        self.fig.canvas.update()

    def on_motion(self, event):
        if self.locked: return
        if LineBuilder.lock is not self: return

        newvector = np.array([event.xdata, event.ydata])
        if event.xdata == None or event.ydata == None: return
        self.roi.addInput(newvector)
        vectordistance = np.linalg.norm(newvector - self.lastvector)
        dotdistance = np.linalg.norm(newvector - self.lastdot)

        if vectordistance > self.vectorthreshold:
            self.roi.addVector(newvector)
            self.lastvector = newvector.copy()
        if dotdistance > self.dotthreshold:
            self.drawDot(newvector, 0)
            self.lastdot = newvector.copy()

    def drawDot(self, vector, type):
        if type == 0:  # is dot
            pass
            #self.ax.plot(vector[0], vector[1], 'ro')
        if type == 1:  # is vector
            pass
            #self.ax.plot(vector[0], vector[1], 'go')

    def on_release(self, event):
        if self.locked: return
        LineBuilder.lock = None
        if self.roi:
            if len(self.roi.vectors) <= 1:
                self.roicount -= 1
                return #if accidently input was just pressed
            self.roi.calculateImage(self.img)
            self.roi = None

        self.cleanUp()

    def cleanUp(self):
        self.line = None

        self.lastvector = np.array([0, 0])
        self.lastdot = np.array([0, 0])

    def on_keyevent(self, event):
        # Locks drawing on the screen
        print('press', event.key)
        if event.key == "i":
            self.locked = not self.locked
