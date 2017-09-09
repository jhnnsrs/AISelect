import math, bioformats
import numpy as np
import javabridge
from bs4 import BeautifulSoup
import logging

from settings import Global


class BioMeta(object):
    def __init__(self, filepath, standalone=True, series=0):

        self.filepath = filepath
        self.date = 0
        self.sizex = 0
        self.sizey = 0
        self.sizez = 0
        self.frames = 0
        self.sizet = 0
        self.sizec = 3
        self.series = 0

        # self.physicalsizet = float(image.find("Pixels").attrs[""])
        self.physicalsizex = 1
        self.physicalsizey = 1
        self.physicalsizexunit = "mm"
        self.physicalsizeyunit = "mm"

        if standalone: javabridge.start_vm(class_path=bioformats.JARS)

        try:
            self.metadata_unparsed = bioformats.get_omexml_metadata(filepath)
            self.metadata = BeautifulSoup(self.metadata_unparsed, "xml")
            # defaultseries
            self.setSeries(series)
            self.query_metadata()
        except:
            raise Exception("BioMeta needs to be run in standalone Mode to initialize Javabridge")
        finally:
            logging.info("BioMeta parsed")

    def getSeriesCount(self):
        return self.seriesamount

    def setSeries(self, it):
        self.series = it
        return self

    def intializeFromTiff(self):

        self.date = "1.3.91"


    def run(self):
        image = self.allmetadata[self.series]
        try:
            print(int(image.find("Pixels").attrs["SizeT"]))
            self.date = str(image.find("AcquisitionDate").contents[0]) if image.find("AcquisitionDate") is not None else "NOT-SET"
            self.sizex = int(image.find("Pixels").attrs["SizeX"]) if image.find("Pixels").attrs["SizeX"] is not None else 0
            self.sizey = int(image.find("Pixels").attrs["SizeY"]) if image.find("Pixels").attrs["SizeY"] is not None else 0
            self.sizez = int(image.find("Pixels").attrs["SizeZ"]) if image.find("Pixels").attrs["SizeZ"] is not None else 0
            self.frames = int(image.find("Pixels").attrs["SizeT"]) if image.find("Pixels").attrs["SizeT"] is not None else 0
            self.sizet = int(image.find("Pixels").attrs["SizeT"]) if image.find("Pixels").attrs["SizeT"] is not None else 0
            self.sizec = int(image.find("Pixels").attrs["SizeC"]) if image.find("Pixels").attrs["SizeC"] is not None else 0

            # self.physicalsizet = float(image.find("Pixels").attrs[""])
            self.physicalsizex = float(image.find("Pixels").attrs["PhysicalSizeX"]) if image.find("Pixels").attrs["PhysicalSizeX"] is not None else 1
            self.physicalsizey = float(image.find("Pixels").attrs["PhysicalSizeY"]) if image.find("Pixels").attrs["PhysicalSizeY"] is not None else 1
            self.physicalsizexunit = image.find("Pixels").attrs["PhysicalSizeXUnit"] if image.find("Pixels").attrs["PhysicalSizeXUnit"] is not None else "Pixels"
            self.physicalsizeyunit = image.find("Pixels").attrs["PhysicalSizeYUnit"] if image.find("Pixels").attrs["PhysicalSizeYUnit"] is not None else "Pixels"
        except:
            print("ITS NOT A VALID BIOIMAGEFILE")
        finally:
            return self

    def query_metadata(self):
        self.allmetadata = self.metadata.findAll("Image")
        self.seriesamount = len(self.allmetadata)

    def getChannelNames(self):

        channelexplain = Global.colorReadableMap
        try:
            channellist = [i.attrs["Name"]+" (" + channelexplain[index]+ ")" for index,i in enumerate(self.allmetadata[self.series].findAll("Channel"))]
            return channellist
        except:
            channellist = [channelexplain[i] for i in range(self.sizec)]
            return channellist

    def getSeriesName(self):
        try:
            seriesname = self.allmetadata[self.series].attrs["Name"]
        except:
            seriesname = "Not Specified"
        return seriesname

    def getDirName(self):
        return "AIS" + self.getFileName()

    def getFileName(self):
        return self.filepath.split("/")[-1].split(".")[0]

    def __str__(self):
        return str(self.allmetadata[self.series])


class BioImageFile(object):
    def __init__(self, filepath, z=None, c=None, channels=None, debug=False):
        # Initialize JAVABRIDGE
        javabridge.start_vm(class_path=bioformats.JARS)

        self.meta = BioMeta(filepath=filepath, standalone=False)

        self.filepath = filepath
        self.layer = z
        self.channels = None
        self.c = c

        # STANDARD SETTINGS HERE
        self.debug = debug
        self.series = 0
        self.setz = 0

        #META
        self.shape = (0,0,0) #TODO: setRoutines
        self.bioshape = (0,0,0)

    def setSeries(self, series=0):
        self.series = series
        self.meta.setSeries(series)
        self.meta.run()
        return self

    def run(self):
        self.ran = True

        # Must be run before Picture is correctly processed
        self.readMeta()
        self.readFile()

        return self

    def getImage(self, z=0, t=0):
        assert (self.ran is True), "BioimageFile has no been instatiated"
        #TODO: THIs is to dirty and needs invastigating
        image = self.file[:, :, :, z, t]
        import scipy.misc
        cvimg = scipy.misc.toimage(image)
        img = np.array(cvimg)
        return img

    def getChannel(self, c=0, z=0, t=0):
        assert (self.ran == True), "BioimageFile has no been instatiated"
        return self.file[:, :, c, z, t]

    def getVideo(self, z=0):
        assert (self.ran == True), "BioimageFile has no been instatiated"
        return self.file[:, :, :, z, :]

    def getZStack(self, t=0):
        assert (self.ran == True), "BioimageFile has no been instatiated"
        file = self.getFile()
        return file[:, :, :, :, t]

    def getZSize(self):
        return self.meta.sizez

    def getSlicedStack(self,start,end, t=0):
        file = self.getFile()
        return file[:,:,:,start:end,t]


    def readFile(self):

        assert (self.ran is True), "BioimageFile has no been instatiated"

        self.file = np.zeros((self.meta.sizex, self.meta.sizey, self.meta.sizec, self.meta.sizez, self.meta.sizet))

        # Debug settings
        tsize = self.meta.sizet if not self.debug else 20
        print(tsize)
        with bioformats.ImageReader(self.filepath, perform_init=True) as reader:
            for c in range(self.meta.sizec):
                for z in range(self.meta.sizez):
                    for t in range(tsize):

                        # bioformats appears to swap axes for tif images and read all three channels at a time for RGB
                        im1 = reader.read(c=c, z=z, t=t, series=self.series, rescale=True, channel_names=None)

                        if im1.ndim == 3:
                            if (im1.shape[2] == 3):
                                # Three channels are red
                                im2 = im1[:, :, c]
                            else:
                                im2 = im1
                        else:
                            im2 = im1
                        if (self.meta.sizex == im2.shape[1]) and (self.meta.sizey == im2.shape[0]):
                            # x and y are swapped
                            #logging.warning("Image might be transposed. Not Swapping")
                            #im3 = im2.transpose()
                            im3 = im2
                        else:
                            im3 = im2


                        self.file[:, :, c, z, t] = im3



        #needs to check if image is in rgb format to display


    def colorMap(self,map):

        emptyfile = np.zeros(self.file.shape)

        if len(map) != self.file.shape[2]:
            map = map[:self.file.shape[2]]
            print("Less then 3 Channels, try different mapping")

        for index, mappedchannel in enumerate(map):
            emptyfile[:,:,index,:,:] = self.file[:,:,mappedchannel,:,:]

        return emptyfile

    def checkDimensions(self,file):
        # unnecessary step

        if file.shape[2] != 3:
            newfile = np.zeros((file.shape[0], file.shape[1], 3, file.shape[3], file.shape[4]))
            newfile[:, :, 1:3, :, :] = file
            file = newfile


        assert self.file.shape[2] == 3, "File Dimensions are wrong"

        return self.file


    def getFile(self):

        print(Global.colorMap)
        self.mappedfile = self.colorMap(Global.colorMap)
       # self.checkedfile = self.checkDimensions(self.mappedfile)

        return self.mappedfile


    def getMeta(self):

        return self.meta

    def readMeta(self):
        self.meta.run()
        pass