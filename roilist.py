from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget

from settings import Global


class RoiListWindow(QWidget):

    def __init__(self):
        super(RoiListWindow,self).__init__()
        Global.roiListWindow = self
        self.setWindowTitle("ROIManager")
        self.layout = QVBoxLayout(self)
        self.roilist = []
        self.lastit = 0

        self.listWidget = QListWidget()
        self.listWidget.setToolTip("Hallo")

        self.layout.addWidget(self.listWidget)
        self.setLayout(self.layout)

    def keyPressEvent(self,event):
        key = event.key()
        print(key)

        if key == QtCore.Qt.Key_Delete:
            Global.handler.deleteROI(self.lastit)



    def listUpdated(self):
        self.listWidget.clear()


        for int,dataset in enumerate(list(zip(Global.roilist,Global.datalist))):

            roi,data = dataset
            item = QtWidgets.QListWidgetItem("Roi %i" % data.index)
            if "Error" in data.flags: item.setBackground(QColor(255,255,0))
            self.listWidget.addItem(item)
            print(int, roi.index,data.index)

        self.updateUI()
        #TODO: Implement META Override

    def roiitemdoubleclicked(self,item):
        it = item.text().split(" ")
        if (len(it) > 1 and it != self.lastit):
            dataindex = [i for i,data in enumerate(Global.datalist) if data.index == int(item.text().split(" ")[1])]
            print(dataindex)
            Global.handler.deleteROI(dataindex[0])
            self.lastit = it

    def roiitemclicked(self,item):
        if item == None: return
        it = item.text().split(" ")
        if len(it) > 1:
            dataindex = [i for i, data in enumerate(Global.datalist) if data.index == int(item.text().split(" ")[1])][0] #should be catched
            if dataindex != self.lastit:
                Global.handler.showData(dataindex)
                self.lastit = dataindex

    def roiitemchanged(self,current,previous):
        self.roiitemclicked(current)
        #placeholder2

    def updateUI(self):
        #self.listWidget.itemClicked.connect(self.roiitemclicked)
        self.listWidget.currentItemChanged.connect(self.roiitemchanged)
        #self.listWidget.itemDoubleClicked.connect(self.roiitemdoubleclicked)
        # DISPLAY META
