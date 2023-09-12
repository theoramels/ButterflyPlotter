# Import the necessary libraries
from PIL import Image as im
import numpy as np
import cv2
import math as m
from g_encoder import GEncoder

printArea = np.array([270, 200]) # (Y, X) in mm
upScale = 2 # upscale factor

# Rescale to fit on designated print area
def reScale(img,upScale):
    res = cv2.resize(img, (0, 0), fx=upScale, fy=upScale)
    A = np.array(res) # convert to np Array
    A = A[:,:,0]*0.2989 + A[:,:,1]*0.5870 + A[:,:,2]*0.1140 # converts to grey scale
    A = A/255 # Invert and normalize between 0 and 1
    return A


img = cv2.imread('test4.jpg') # read in image

# Rescale
A = reScale(img,upScale)



A = np.round(((A-np.amin(A))/np.amax(A))*255) # normalize between 0 and 255
A = A.astype(np.uint8) # cast into proper data type
#output = np.dstack((A,A,A))

print(A.shape)
# Horizontal derivitive
Ahorz = A
filt = np.array([-1,1])
for Y in range(Ahorz.shape[0]):
    row = np.convolve(Ahorz[Y,:],filt,mode='same')
    Ahorz[Y,:] = row

# save
data = im.fromarray(A) # creating image object of array
data.save('testProcessed.png') # saving the final output 




print(A.shape)