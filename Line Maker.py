# Import the necessary libraries
from PIL import Image as im
import numpy as np
import cv2

printArea = (1000, 1880) # (Y, X) in mm
lineDist = 10 # distance between lines in mm
blurLen = 8

upSample = 1

img = cv2.imread('test.jpg')

# Resize image to print volume size wtihout distorting
scaleY = (printArea[0] / img.shape[0])*upSample
scaleX = (printArea[1] / img.shape[1])*upSample
if (scaleY < scaleX):
    upScaleSz = (round(img.shape[1]*scaleY), round(img.shape[0]*scaleY))
else:
    upScaleSz = (round(img.shape[1]*scaleX),round(img.shape[0]*scaleY))

res = cv2.resize(img, dsize=upScaleSz, interpolation=cv2.INTER_CUBIC)
A = np.array(res) # convert to np Array
A = A[:,:,0]*0.2989 + A[:,:,1]*0.5870 + A[:,:,2]*0.1140 # converts to grey scale

# blur image
filt = np.ones(blurLen)/blurLen
# Blur image row by row
for n in range(blurLen):
    for Y in range(0,A.shape[0]):
        row = np.convolve(A[Y,:],filt,mode='same')
        A[Y,:] = row



# make a new array to become the line image
L = np.ones(A.shape)*255



# loop though and add lines
prevHeight = 0
for Y in range(lineDist, round((A.shape[0]/upSample)-1)*upSample, lineDist*upSample):
    prevShift = 0
    for X in range(0,A.shape[1]):
        shift = round(((A[Y,X] / -255)+1) * lineDist*upSample*0.7)
        if prevShift-shift < 0:
            for n in range(prevShift,shift):
                L[Y-n,X] = 0
        elif prevShift - shift > 0:
            for n in range(prevShift,shift,-1):
                L[Y-n,X] = 0
        else:
            L[Y-shift,X] = 0
        prevShift = shift



A = np.around(((A-np.amin(A))/np.amax(A))*255) # normalize between 0 and 255
A = A.astype(np.uint8) # cast into proper data type



L = L.astype(np.uint8) # case into proper data type
output = np.dstack((L,L,L))
# save
data = im.fromarray(output) # creating image object of array
data.save('testProcessed.png') # saving the final output 


