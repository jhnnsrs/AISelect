import cv2

from settings import Global
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

def void(image):
    print("DONE VOID")
    return image

def laplace(image):
    print("LaPlacian of  Selective Channel")
    image = image[:, :, Global.selectiveChannel]
    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    return laplacian

def channel(image):
    print("Only display channel", Global.selectiveChannel)
    images = image[:, :, Global.selectiveChannel]

    return images


def overlap(image):
    max = np.max(image)
    threshold = Global.overlapthreshold * max
    overch1 = [1 if i == True else 0 for i in (image[:,:, 0] > threshold).flatten()]
    overch2 = [1 if i == True else 0 for i in (image[:,:, 1] > threshold).flatten()]

    both = np.add(overch2,overch1)
    newimage = [max if i == 2 else 0 for i in both]
    newimage = np.array(newimage).reshape((image.shape[0],image.shape[1]))

    #imager = np.zeros(image.shape, np.uint8)

    return newimage

def canny(image):
    cvimage = image[:, :, Global.selectiveChannel]
    blured = cv2.GaussianBlur(cvimage, (3, 3), 3)
    sobelx = cv2.Canny(blured, 100, 200)

    return sobelx


def color(image):
    print("Display real representation", Global.selectiveChannel)
    imager = np.zeros(image.shape, np.uint8)
    imager[:,:,Global.selectiveChannel] = image[:,:,Global.selectiveChannel]

    return imager


def sobel(image):
    print("Sobel of AIS-Channel")
    image = image[:, :, Global.selectiveChannel]
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    return sobelx

def laplaceofgaussian(image):
    return image