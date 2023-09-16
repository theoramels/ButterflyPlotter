# Import the necessary libraries
from PIL import Image as im
import numpy as np
import cv2
import math as m
from g_encoder import GEncoder

printArea = np.array([950, 1880]) # (Y, X) in mm
upScale = 20 # upscale factor
blurLen = 10

lineSpace = 2 # distance between lines in mm
lineHeight = 1 # max amplitude of sinwave
lineDensity = .2 # mm per point that lines are made out of


img = cv2.imread('Picture3.png') # read in image

# Rescale to fit on designated print area
def reScale(img,printArea,upScale):
    # Resize image to print volume size wtihout distorting
    scaleY = (printArea[0] / img.shape[0])*upScale
    scaleX = (printArea[1] / img.shape[1])*upScale
    if (scaleY < scaleX):
        upScaleSz = (round(img.shape[1]*scaleY), round(img.shape[0]*scaleY))
    else:
        upScaleSz = (round(img.shape[1]*scaleX),round(img.shape[0]*scaleX))

    res = cv2.resize(img, dsize=upScaleSz, interpolation=cv2.INTER_CUBIC)
    A = np.array(res) # convert to np Array

    A = A[:,:,0]*0.2989 + A[:,:,1]*0.5870 + A[:,:,2]*0.1140 # converts to grey scale
    A = np.round(A)
    printArea = printArea*upScale
    if (scaleY < scaleX):
        filler = 255*np.ones((printArea[0],round((printArea[1] -A.shape[1])/2)))
        A = np.hstack((filler,A,filler))
    else:
        filler = 255*np.ones((round((printArea[0] -A.shape[0])/2),printArea[1]))
        A = np.vstack((filler,A,filler))

    return A

# DEFINE FUNCTIONS-------------------------
# generate horizontal lines
def HorzLines(printArea,lineDensity):
    yRange = np.arange(0,printArea[0]-1,lineSpace) # Y coordinates
    xRangeForward = np.arange(0, printArea[1]-1,lineDensity) # X coordinates left to right
    xRangeBackward = np.arange(printArea[1]-1,0,-lineDensity) # X coordinates right to left
    line = np.ones((len(yRange)*len(xRangeForward),2)) # (X,Y)
    l = xRangeForward.shape[0]
    for idx in range(yRange.shape[0]):
        r = np.arange(l*idx,(idx+1)*l)
        if idx%2:
            line[r,0] = xRangeForward
        else:
            line[r,0] = xRangeBackward
        line[r,1] = np.ones(l)*yRange[idx]
    return line


# Rescale to fit on designated print area
A = reScale(img,printArea,upScale)

A = A/-255 + 1 # Invert and normalize between 0 and 1
# blur image
filt = np.ones(blurLen)/blurLen
# Blur image row by row
for n in range(3):
    for Y in range(0,A.shape[0]):
        row = np.convolve(A[Y,:],filt,mode='same')
        A[Y,:] = row

# generate line pattern
line = HorzLines(printArea,lineDensity)

def myDist(line,input):
    dist = np.zeros((line.shape[0],1))
    for n in range(line.shape[0]):
        coord = line[n]
        dist[n] = np.linalg.norm(coord-input)
    return(dist)


# sample image to determine sinusoid amp and freq
for n in range(line.shape[0]):
    scaledCord = (round(line[n,1]*upScale),round(line[n,0]*upScale))
    pxl = A[scaledCord]
    line[n,1] = line[n,1] + lineHeight*pxl * m.sin(3*line[n,0]+pxl*2)

# remove straight line points
speedyLine = []
prevY = -1
for n in range(line.shape[0]-1):
    futureY = line[n+1,1]
    if not((abs(prevY - line[n,1]) < 0.05) and (0.05 > abs(futureY - line[n,1]))):
        speedyLine.append((line[n,0],line[n,1]+1000-printArea[0]-lineSpace))
    prevY = line[n,1]

# convert to python lists so alexs code doesn't shit a brick
#lineOut = []
#for row in line:
#    lineOut.append((row[0],row[1]))
out = []
out.append(speedyLine)
# convert to Gcode
encoder = GEncoder()
with open('lines.gcode', "w") as f:
    encoder.encode(out, f)

A = np.around(((A-np.amin(A))/np.amax(A))*255) # normalize between 0 and 255
A = A.astype(np.uint8) # cast into proper data type
output = np.dstack((A,A,A))

# save
data = im.fromarray(output) # creating image object of array
data.save('testProcessed.png') # saving the final output 


