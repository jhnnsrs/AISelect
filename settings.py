#  This file is part of AISelect.

#  AISelect is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  AISelect is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with AISelect.  If not, see <http://www.gnu.org/licenses/>.


import random
from itertools import cycle

import numpy as np
from matplotlib import cm

from randcolours import rand_cmap


class Global(object):

    overlapthreshold = 0.4
    flagsSeperator = "; "
    selectiveChannel = 0
    colorMap = [0, 1, 2]
    colorReadableMap = ["R","G","B"]
    availableMaps = [[0,1,2],[0,2,1],[1,2,0],[1,0,2],[2,0,1],[2,1,0]]
    availableReadableMaps = [["R","G","B"],["R","B","G"],["G","B","R"],["G","R","B"],["B","R","G"],["B","G","R"]]
    threshold = 0.2
    startstack = 0 # needs to be set before image is displayed
    endstack = None # needs to be set before anything
    font = {'family': 'sans-serif', 'color':  'black','weight': 'bold','size': 9}
    bbox = dict(boxstyle="circle,pad=0.2", fc="white", ec="white", lw=2, alpha=0.8)
    saveVolumetricInfo = False
    colours = iter((rand_cmap(200)(np.linspace(0, 1, 200))))
    bioImageFile = None
    imageWindow = None
    settingsWindow = None
    roiListWindow = None
    metaWindow = None
    roiWindow = None
    series = 0
    dirname = "AIS"
    filename = ""

    handler = None
    image = None
    roilist = []
    datalist = []
    lastROI = None

    aischannel = 0
    flags = []

    meta = None
    stack = None
    filepath = ""
    postprocess = None
    projection = None
    projected = None



