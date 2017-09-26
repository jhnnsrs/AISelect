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


import numpy as np
import matplotlib.pyplot as plt
from misc import toimage

def tonumpy(image):
    cvimg = toimage(image)
    img = np.array(cvimg)
    print("ARGMAX " + str(img.max()))
    return img

def void(stack):
    print("STACKED",stack.shape)
    return tonumpy(stack[:,:,:,0])
    #TODO: THIs is to dirty and needs invastigating


def maxisp(stack):
    print(stack.shape)
    if stack.shape[3] == 0:
        print("Already Projected")
        return tonumpy(stack[:,:,:])
    maxproj = np.nanmax(stack, axis=3)
    print("MAXISP", maxproj.shape)
    return tonumpy(maxproj)


def average(stack):
    averageproj = stack

    return averageproj


def minimum(stack):
    minimumproj = stack

    return minimumproj