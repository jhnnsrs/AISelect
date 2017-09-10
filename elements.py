
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import numpy as np
import cv2
from matplotlib.path import Path

from settings import Global
from bioimage import BioMeta

class Roi(object):

    def __init__(self,roindex):
        self.newLabelCallback = None
        self.flags = []
        self.inputvectors = []
        self.index = roindex
        self.nvectors = 0
        self.vectors = []
        self.width = 10
        self.totalwidth = 0
        self.roiimage = None
        self.scale = 10
        self.colour = next(Global.colours)
        self.img = None
        self.boxes = [] #Should if handled correctly always be length self.vectors - 1
        self.patcheslink = []
        self.nchannels = 3 #used to be from Meta, but pictures are always with 3 channels TODO: prettify

        print("THE COLOUR IS",self.colour)

        if self.roiimage == None:
            width = 0
            height = self.scale * 2
            self.roiimage = np.empty((height,width,self.nchannels))

        self.newBoxCallback = None
        self.imageCallback = None
        self.roiCallback = None

    def setNewBoxCallback(self,callback):
        '''Returns newly creaty Box'''
        self.newBoxCallback = callback

    def setNewLaberCallback(self,callback):
        self.newLabelCallback = callback
    def setRoiCallback(self,callback):
        self.roiCallback = callback

    def setImageCallback(self,callback):
        self.imageCallback = callback

    def addInput(self,vector):
        self.inputvectors.append(vector)

    def addVector(self,vector):
        self.vectors.append(vector)
        self.nvectors += 1

        if self.nvectors > 1:
            self.calculateNewBox()

    def setWidth(self,width):
        self.width = width

    def getHDF5(self):
        #TODO: Should return ROI-Data
        pass

    def _getScaledOrtho(self,a):
        #get perpendicular
        perp = np.empty_like(a)
        perp[0] = -a[1]
        perp[1] = a[0]

        perpnorm = perp / np.linalg.norm(perp)
        perpscaled = perpnorm * self.scale
        return perpscaled

    def _getBoxDim(self,pos):
        '''Index 0 Box is between 0 and 1 Vector'''
        if pos > (len(self.vectors)-1): raise Exception("Not enough Vectors")

        vectors = np.array(self.vectors)

        a = vectors[pos]
        b = vectors[pos+1]


        #perpold = self.getScaledPerp(old - a)
        perpnew = self._getScaledOrtho(a - b)

        c1 = a + perpnew
        c2 = a - perpnew
        c3 = b - perpnew
        c4 = b + perpnew

        width = np.linalg.norm(a - b)
        verts = [c1, c2, c3, c4]
        return verts,width

    def getRoiImage(self):
        if not self.roiimage: raise Exception("No Image Yet Constructed")
        return self.roiimage

    def getWidthFromScatter(self,pointa, pointb):
        pix = np.arange(self.bioimage.shape[0])
        piy = np.arange(self.bioimage.shape[1])
        xv, yv = np.meshgrid(pix, piy)
        pixels = np.vstack((xv.flatten(), yv.flatten())).T
        verts = [pointa,pointb]
        codes = [Path.MOVETO,Path.LINETO]
        path = Path(verts,codes)
        selection = path.contains_points(pixels, radius=1)

        return sum(selection)



    def _getTranslatedPicture(self,box,width=None,height=None,):

        if not height: height = self.scale * 2
        if not width: width = np.linalg.norm(box[1]-box[2])
        self.totalwidth += width

        pts1 = np.float32(box)
        pts2 = np.float32([[0, height],[0, 0],[width, 0],[width, height]])

        M = cv2.getPerspectiveTransform(pts1, pts2)

        dst = cv2.warpPerspective(self.bioimage, M, (int(round(width)), int(height)))

        return dst

    def addToRoiImage(self, new):
        #TODO: THIS SHOULD BE WAY FASTER???

            #TODO: MAKE THIS COMPLETLY EMPTY

        old = self.roiimage
        ha, wa = old.shape[:2]
        hb, wb = new.shape[:2]
        channels = old.shape[2] #can be either
        max_height = np.max([ha, hb])
        total_width = wa + wb

        new_img = np.zeros(shape=(max_height, total_width,channels), dtype=np.uint8)
        new_img[:ha, :wa] = old
        new_img[:hb, wa:] = new

        self.roiimage = new_img

    def calculateNewBox(self):
        self.boxes.append(self._getBoxDim(self.nvectors-2)) #still uglys


        if self.newBoxCallback: self.newBoxCallback(self.boxes[-1], tuple(self.colour))

    def calculateImage(self,image = Global.projected):
        self.bioimage = image
        boxlength = len(self.boxes)
        called = False

        for i,box in enumerate(self.boxes):
            verts, width = box
            newpicture = self._getTranslatedPicture(verts)
            self.addToRoiImage(newpicture)
            # might not be the right spot but fuck it
            if i > boxlength/2 and not called:
                if self.newLabelCallback: self.newLabelCallback(verts)
                called = True


        self.bioimage = None
        #Garbage Collection


        if self.imageCallback: self.imageCallback(self.roiimage)
        if self.roiCallback: self.roiCallback(self)


class AcquiredData(object):

        def __init__(self):
            self.index = 0
            self.aislength = 0
            self.piclength = 0
            self.picheight = 0
            self.aisstart = 0
            self.aisend = 0
            self.b4channel = 0
            self.threshold = 0
            self.method = "MinMax-Search"
            self.vectorlength = 0
            self.colour = ""

            self.stagestart = 0
            self.stageend = 0

            self.roiimage = None
            self.intensitycurves = [] #shape (length,values,amountchannels)
            self.aisphysicallength = 0
            self.aisphysicalstart = 0
            self.aisphysicalend = 0
            self.thresholdvalue = 0 #should not be the percent but real threshold value
            self.comment = 0
            self.flags = []
            self.parsingmethod = "RoiParser1.0"




class RoiParser(object):

    def __init__(self):
        pass

    @staticmethod
    def parseRoi(roi: Roi, meta: BioMeta = Global.meta, environment = Global):


        data = AcquiredData()
        data.piclength = roi.roiimage.shape[1]
        data.picheight = roi.roiimage.shape[0]
        data.roiimage = roi.roiimage
        data.colour = roi.colour
        data.index = roi.index
        data.b4channel = environment.aischannel
        data.vectorlength = roi.totalwidth
        data.stagestart = environment.startstack
        data.stageend = environment.endstack

        #print(roi.roiimage.shape)
        height = data.picheight

        middleup = int(height / 2 - 3)
        middledown = int(height / 2 + 3)

        bild = data.roiimage[middleup:middledown, :, :]

        np.seterr(divide='ignore', invalid='ignore') # TODO: FREE THE CUPRIT
        #print(roi.totalwidth,data.piclength)
        averages = np.max(bild, axis=0)
        intensity = averages / averages.max(axis=0)

        data.intensitycurves = intensity

        physizex = environment.meta.physicalsizex #ATTENTION IF NOT SAME RATIO VOXEL IS FUCKED UP
        physizey = environment.meta.physicalsizey

        c = environment.aischannel
        threshold = environment.threshold
        overindices = (intensity[:, c] > threshold).nonzero()[0]
        if (len(overindices)<2):
            overindices = np.array([0,data.piclength]) #TODO: needs to be handled
            data.flags.append("Error")
            print("ERROR ON AIS")

        data.flags = data.flags + Global.flags
        xstart = overindices.min()
        ystart = overindices.max()

        if environment.saveVolumetricInfo is True:
            height, ystart, yend = RoiParser.calculateVolumetricData(roi,xstart,environment)

        data.aisstart = xstart
        data.aisend = ystart
        data.aislength = ystart - xstart
        data.aisphysicallength = data.aislength * float(physizex)
        print(data.aislength,physizex,data.aisphysicallength)
        data.threshold = threshold


        return data

    @staticmethod
    def calculateVolumetricData(roi,xstart,environment):

        image = roi.roiimage
        threshold = environment.threshold
        c = environment.aischannel

        averages = np.max(image, axis=0)
        intensity = averages / averages.max(axis=0)


        overindices = (intensity[:, c] > threshold).nonzero()[0]
        if (len(overindices) < 2):
            overindices = np.array([0, data.piclength])  # TODO: needs to be handled
            data.flags.append("Error")
            print("ERROR ON AIS")

        data.flags = data.flags + Global.flags
        xstart = overindices.min()
        ystart = overindices.max()





class CallbackSelector(QtWidgets.QComboBox):

    def __init__(self):
        super(CallbackSelector,self).__init__()
        self.callbacklist = []
        self.itemsToAdd()

        self.currentIndexChanged.connect(self.selectionChanged)

    def itemsToAdd(self):
        pass

    def setCallback(self,callback):

        #TODO Must be inherited
        pass

    def selectionChanged(self,i):
        print(self.itemText(i), i)
        self.setCallback(self.callbacklist[i])

    def newItem(self,name,callback):
        self.addItem(name)
        self.callbacklist.append(callback)


