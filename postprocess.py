import cv2

from settings import Global


def void(image):
    print("DONE VOID")
    return image

def laplace(image):
    print("LaPlacian of b4Channel")
    image = image[:, :, Global.aischannel]
    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    return laplacian


def sobel(image):
    print("Sobel of AIS-Channel")
    image = image[:, :, Global.aischannel]
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    return sobelx

def laplaceofgaussian(image):
    return image