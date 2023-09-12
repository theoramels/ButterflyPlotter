# Import the necessary libraries
import numpy as np
import cv2
from scipy import signal
from tempfile import TemporaryFile
import colorsys
import math as m

printArea = np.array([270, 200]) # (Y, X) in mm
upScale = 10 # upscale factor

# find gradient of the image
def gradient(img,upScale):
    
    def gkern(l=5, sig=1.):
        ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
        gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
        kernel = np.outer(gauss, gauss)
        return kernel / np.sum(kernel)

    # Rescale to fit on designated print area
    def reScale(img,upScale):
        img = cv2.resize(img, (0, 0), fx=upScale, fy=upScale)
        A = np.array(img) # convert to np Array
        A = A[:,:,0]*0.2989 + A[:,:,1]*0.5870 + A[:,:,2]*0.1140 # converts to grey scale
        filt = gkern(upScale*2,upScale)
        A = signal.convolve(A,filt,mode='valid')
        A = A/255 # Invert and normalize between 0 and 1
        return A


    def myNorm(output):
        output = (output-np.amin(output))
        output = output/np.amax(output)
        return output


    # Rescale
    A = reScale(img,upScale)
    
    kern = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
    Ahorz = signal.convolve(A,kern,mode='valid')
    kern = np.array([[-1,-1,-1],[0,0,0],[1,1,1]])
    Avert = signal.convolve(A,kern,mode='valid')
    Atheta = np.arctan2(Ahorz,Avert+0.000001)
    Amag = np.sqrt(np.power(Avert,2) + np.power(Ahorz,2))

    dy = m.floor((A.shape[0] - Avert.shape[0])/2)
    dx = m.floor((A.shape[1]-Avert.shape[1])/2)
    A = A[dy:(Avert.shape[0]+dy),dx:(Avert.shape[1]+dy)]
    
    # Rectangular format:
    # Ahorz : horizontal component of the derivitive of the image
    # Avert : vertical component of the derivitive of the image
    # 
    # Polar format:
    # Atheta : angle of the derivitive of the image
    # Amag : magnitude of the derivitive of the image
    return A, Ahorz, Avert, Atheta, Amag

img = cv2.imread('test2.jpg') # read in image

A, Ahorz, Avert, Atheta, Amag = gradient(img,upScale)

All = np.dstack((A,Ahorz,Avert,Atheta,Amag)) # stack
np.save('Gradient.npy', All) # and save

Atheta = (Atheta + 3.14159)/(2*3.14159) # normalize between 0 and 1
Acolors = np.zeros((Atheta.shape[0], Atheta.shape[1], 3))
for y in range(Atheta.shape[0]):
    for x in range(Atheta.shape[1]):
        [r,g,b] = colorsys.hsv_to_rgb(Atheta[y,x], 1, 1)
        Acolors[y,x,:] = [r,g,b]

output = Acolors*255
#output = np.round(myNorm(output)*255)
cv2.imwrite('testProcessed.png',output)


