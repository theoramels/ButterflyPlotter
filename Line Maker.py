# Import the necessary libraries
from PIL import Image as im
import numpy as np
import cv2
from g_encoder import GEncoder

printArea = (200, 250) # (Y, X) in mm

lineDist = 2 # distance between lines in mm
lineHeight = 1.5 # line height in mm
# poo poo pee pee


blurLen = 2
start = 0
img = cv2.imread('test5.jpg')

# Resize image to print volume size wtihout distorting
scaleY = (printArea[0] / img.shape[0])
scaleX = (printArea[1] / img.shape[1])
if (scaleY < scaleX):
    upScaleSz = (round(img.shape[1]*scaleY), round(img.shape[0]*scaleY))
else:
    upScaleSz = (round(img.shape[1]*scaleX),round(img.shape[0]*scaleX))

res = cv2.resize(img, dsize=upScaleSz, interpolation=cv2.INTER_CUBIC)
A = np.array(res) # convert to np Array
A = A[:,:,0]*0.2989 + A[:,:,1]*0.5870 + A[:,:,2]*0.1140 # converts to grey scale

if (scaleY < scaleX):
    filler = 255*np.ones((printArea[0],round((printArea[1] -A.shape[1])/2)))
    A = np.hstack((filler,A,filler))
else:
    filler = 255*np.ones((round((printArea[0] -A.shape[0])/2),printArea[1]))
    A = np.vstack((filler,A,filler))

print(A.shape)
A = A/-255 + 1 # Invert and normalize between 0 and 1
# blur image
filt = np.ones(blurLen)/blurLen
# Blur image row by row
for n in range(3):
    for Y in range(0,A.shape[0]):
        row = np.convolve(A[Y,:],filt,mode='same')
        A[Y,:] = row


# loop though and add lines
all = []
line = []
lineNum = 0
for Y in range(lineDist-start, round((A.shape[0])-1)-start, lineDist):
    lineNum = lineNum + 1
    #line = []
    prevShift = 0
    if (lineNum % 2) == 0:
        iterat = range(0,A.shape[1])
    else:
        iterat = range(A.shape[1]-1,-1,-1)

    for X in iterat:
        shift = (A[Y,X])
        if (abs(prevShift-shift) > lineHeight/255) or X==A.shape[1]-1 or X==0:
            firstTime = 0
            line.append((X,(1000 - printArea[0]) + Y + shift*lineHeight))
        prevShift = shift
    
    if lineNum < 2:
        all.append(line)
all.append(line)
encoder = GEncoder()
with open('lines.gcode', "w") as f:
    encoder.encode(all, f)

A = np.around(((A-np.amin(A))/np.amax(A))*255) # normalize between 0 and 255
A = A.astype(np.uint8) # cast into proper data type
output = np.dstack((A,A,A))
# save
data = im.fromarray(output) # creating image object of array
data.save('testProcessed.png') # saving the final output 


