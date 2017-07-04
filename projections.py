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
    maxproj = np.nanmax(stack, axis=3)
    print("MAXISP", maxproj.shape)
    return tonumpy(maxproj)


def average(stack):
    averageproj = stack

    return averageproj


def minimum(stack):
    minimumproj = stack

    return minimumproj