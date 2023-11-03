# Import the necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import cv2
import math as m
import random
from scipy import signal

dMinMax = (.5,4) # (mm) min and max distance between lines
printArea = (200,270) # (x,y) in mm
pixelsPerMM = 10 # pixels per mm
fname = 'test2.jpg' # input image file name
L= 100000 # max itterations

# pre generate list of circles to use later
def CircleGenerator(dMinMax,pxl_mm):
    sz = m.ceil(dMinMax[1]*np.amax(pxl_mm))+1 # the +1 stopped out of bounds errors happening idx why
    circle = np.zeros((sz*2+1, sz*2+1, sz)) # initiate cube of zeros
    circle[sz+1, sz+1,0] = 1 # color in center pixel
    for rad in range(1,circle.shape[2]):
        circle[:,:,rad] = circle[:,:,rad-1] # start with previous circle size
        for theta in np.linspace(-m.pi, m.pi, 10000):
            x = round(m.cos(theta)*rad+sz+1)
            y = round(m.sin(theta)*rad+sz+1)
            circle[x,y,rad] = 1 # increase radius
    # trim off edges
    c = []
    for n in range(circle.shape[2]):
        idx = np.where(circle[sz+1,:,n] == 1)
        idx = idx[0]
        if n == 0:
            c.append(circle[idx,idx,n])
        else:
            c.append(circle[idx[0]:idx[-1]+1, idx[0]:idx[-1]+1,n])

    return c # list containing all the sizes of circles you could ever want

def imagePreprocess(fname,printArea, pxl_mm):
    # Gaussian kernel generator
    def gkern(l=5, sig=1.):
        # l : length of nxn array
        # sig : standard deviation of gaussian array, in units of pixels i think?
        ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
        gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
        kernel = np.outer(gauss, gauss)
        return kernel / np.sum(kernel)

    A = cv2.imread(fname) # read in image
    A = A[:,:,0]*0.2989 + A[:,:,1]*0.5870 + A[:,:,2]*0.1140 # converts to grey scale
    A = A/255 # scale between 0 and 1
    ARin = A.shape[1]/A.shape[0] # x/y
    ARout = printArea[0]/printArea[1] #x/y
    if ARin < ARout:
        # scale verticaly
        scf = A.shape[0]/printArea[1]
        extra = m.ceil(printArea[0]*scf)-A.shape[1]
        filler = np.ones((A.shape[0],m.ceil(extra/2)))
        A = np.hstack((filler,A,filler))
    else:
        # scale horizontaly
        scf = A.shape[1]/printArea[0]
        extra = m.ceil(printArea[1]*scf)-A.shape[0]
        filler = np.ones((m.ceil(extra/2),A.shape[1]))
        A = np.vstack((filler,A,filler))

    # 2d pixel density
    curPxl_mm = m.sqrt((A.shape[0]*A.shape[1])/(printArea[0]*printArea[1]))
    upScale = (pxl_mm/curPxl_mm) # up scale factor
    newShape = (m.ceil(upScale*A.shape[1]), m.ceil(upScale*A.shape[0]))
    A = cv2.resize(A, newShape) # up scale image
    filt = gkern(round(upScale*3),round(upScale)) # blur filter
    A = signal.convolve(A,filt,mode='same') # blur
    A = A[-1:0:-1,:] # flip so image ends up right side up
    px_mm = np.array(((A.shape[1]-1)/printArea[0], (A.shape[0]-1)/printArea[1])) # true pixels per mm after rescaling and rounding things (x,y)
    return A, px_mm

class rover:
    def __init__(self, initialPosition, step, L, pxl_mm, bordWidth, dMinMax, printArea):
        self.step = step # step size (mm)
        self.pxl_mm = np.amin(pxl_mm)
        self.bordWidth = bordWidth # width of border on Trace
        self.printArea = printArea # print Area
        self.stampDelay = m.ceil(dMinMax[1]/step) # delay to stamp behind the thing. includes saftey factor
        self.pos = np.ones((L+1,3))*-69 # initiate position array for speed
        self.pos[0,:] = np.array(initialPosition) # assign initial position
        self.n = 0 # counter to keep track of where in the position array we are
        self.edgeFound = 1 # edge found flag
        self.alpha = 1 # tracing direction (cw : 1 or ccw : -1) these could be switched i have no idea and do not care
        self.switchCount = 0 # steps since last switch
        self.boundsSwitch = 1 # flag to keep from bouncing getting stuck when respawning on the edges while still being able to bounce of the edges

    def move(self,d,Trace): # d : distance from other lines
        rotation = m.pi/180 # step size to rotate (pi/180) is one degree
        senseLen = self.step # length to probe out in front (mm)
        theta = self.pos[self.n,2] # current direction facing
        
        def sampleTrace(theta,senseLen):
            xSamp = self.pos[self.n,0] + m.cos(theta)*senseLen # calc x pos place to sample
            xSamp = round(xSamp*self.pxl_mm) + self.bordWidth # convert to pixels
            ySamp = self.pos[self.n,1] + m.sin(theta)*senseLen # calc y pos place to sample
            ySamp = round(ySamp*self.pxl_mm) + self.bordWidth # convert to pixels
            samp = Trace[xSamp,ySamp]
            return samp
        

        weight = (d-dMinMax[0])/(dMinMax[1]-dMinMax[0]) # scales darkness level from 0 to 1
        weight = -weight + 1 # inverts dark values to be at 1
        # randomly switch directions
        # if within bounds by toler
        toler = .1 # distance to be within bounds by in mm
        if self.pos[self.n,0] > toler and self.pos[self.n,0] < self.printArea[0]-toler and self.pos[self.n,1] > toler and self.pos[self.n,1] < self.printArea[1]-toler:
            self.boundsSwitch = self.boundsSwitch + 1
            if random.random() < weight*0.0001 and self.switchCount > self.stampDelay*2: 
                self.alpha = self.alpha*-1 # switch directions
                self.switchCount = 0 # reset counter till next switch allowed
        else: # if outside of bounds
            if self.boundsSwitch > 30:
                self.alpha = self.alpha*-1 # switch directions
                self.boundsSwitch = 0
                # print('BOunced Big GOIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')

        # if inside orange box
            # set flag = 0
        # else
            # if flag is 0
                # switch directions
                # set flag to 1
        

        
        sInit = sampleTrace(theta,senseLen) # initial sample of Trace
        self.edgeFound = 0 # edge found flag
        for mult in range(1,8):
            for n in range(360):
                s = sampleTrace(theta, mult*senseLen) # sample Trace
                theta = theta + self.alpha*(s-0.5)*2*rotation # rotate appropriate direction. (s-0.5)*2 makes it either -1 or 1
                if s != sInit: # repeat until Sample changes "color"
                    self.edgeFound = 1
                    break # then break out of loop
            if self.edgeFound == 1:
                break

        x = self.pos[self.n,0] + m.cos(theta)*self.step # calc new x position
        y = self.pos[self.n,1] + m.sin(theta)*self.step # calc new y position
        newPos = np.array((x,y,theta))

        self.n = self.n+1 # increment in array
        self.switchCount = self.switchCount + 1 # increment steps since last switch counter
        self.pos[self.n,:] = newPos # save new position

    def stamp(self,d,Trace,c): # distance from other lines
        if n > self.stampDelay:
            curPos = np.round(self.pos[self.n-self.stampDelay,:]*self.pxl_mm) + self.bordWidth # convert from mm to pxls
            curPos = curPos.astype(int)
        
            radius = m.floor(d*self.pxl_mm) # converts to pixles
            width = round((c[radius].shape[0]-1)/2) # width of stamp
            x = (curPos[0]-width, curPos[0]+width+1) # column indicers of Trace to stamp
            y = (curPos[1]-width, curPos[1]+width+1) # row indicies of Trace to stamp
            mask = np.logical_or(Trace[x[0]:x[1], y[0]:y[1]], c[radius]) # OR circle with Trace
            Trace[x[0]:x[1], y[0]:y[1]] = mask # assign ORed stamp to Trace
            if x[0] < self.bordWidth or x[1] > (self.bordWidth + Trace.shape[0]) or y[0] < self.bordWidth or y[1] > (self.bordWidth + Trace.shape[1]):
                Trace[:bordWidth,:] = 0 # add border
                Trace[-bordWidth:,:] = 0
                Trace[:,:bordWidth] = 0
                Trace[:,-bordWidth:] = 0
            # make it into four elseif statements for speed


# Read in Image and scale appropriatly
A, pxl_mm = imagePreprocess(fname,printArea, pixelsPerMM)
# pre generate a list of circles to use later
c = CircleGenerator(dMinMax,pxl_mm)

print((A.shape[1],A.shape[0]))
print((printArea[0]*pxl_mm[0],printArea[1]*pxl_mm[1]))


# initiate the Trace matrix
bordWidth = c[-1].shape[0]*2 # width of border. This is twice as big as it should ever need to be but whatever
Trace = np.zeros((A.shape[1]+bordWidth*2,A.shape[0]+bordWidth*2)) # initiate trace matrix (x,y)


p = (0.5, 0.5) # initial position of the thing. (normalized coords) (0.5,0.5) == dead center
idx = (round(p[0]*printArea[0]*pxl_mm[0]) + bordWidth, round(p[1]*printArea[1]*pxl_mm[1]) + bordWidth)

posInit = (p[0]*printArea[0], p[1]*printArea[1], 0) # initial position based on p
step = dMinMax[0] # step distance (mm)
r = [] # initiate list of rovers
r.append(rover(posInit,step,L,pxl_mm,bordWidth,dMinMax,printArea)) # make an instance of the class
# adding starting runway to trace
Trace[idx[0]:idx[0]+m.ceil(dMinMax[0]*pxl_mm[0]), idx[1]:idx[1]+m.ceil(r[0].stampDelay*pxl_mm[0])] = 1

# here we go
for x in range(80): # loop that respawns rover when it gets stuck
    for n in range(L): # loop that steps the rover forward

        if r[x].pos[r[x].n,0] > printArea[0]:
            r[x].pos[r[x].n,0] = printArea[0]
        if r[x].pos[r[x].n,1] > printArea[1]:
            r[x].pos[r[x].n,1] = printArea[1]
        coords = np.round(np.array((r[x].pos[r[x].n,0]*pxl_mm[0], r[x].pos[r[x].n,1]*pxl_mm[1]))) # coordinates to sample the input image (pixels)
        coords = coords.astype(int)
        samp = A[coords[1],coords[0]] # sample image (y,x)
        d = samp*(dMinMax[1]-dMinMax[0]) + dMinMax[0]
        r[x].move(d,Trace)
        # if n%100 == 0:
            # print('LoopNum: ' + str(n) + '    Cords: ' + str(r[x].pos[r[x].n,:]))
        if r[x].edgeFound == 0:
            break
        r[x].stamp(d,Trace,c)
    r[x].pos = r[x].pos[r[x].pos[:,0] != -69,:] # get rid of unused initiated parts
    
    # check if Trace is filled
    filled = np.sum(Trace)/((Trace.shape[0]-bordWidth*2)*(Trace.shape[1]-bordWidth-2))
    print(filled)
    if filled > 0.9:
        break

    # determine respawn point radialy
    xCord = round(p[0]*Trace.shape[0])
    for yCord in range(Trace.shape[1]):
        if Trace[xCord, yCord] == 1:
            break
    # for theta in np.linspace(0,2*m.pi,360):
    #     for radius in range(np.max(Trace.shape)*2):
    #         xCord = round(radius*m.cos(theta) + Trace.shape[0]*p[0])
    #         yCord = round(radius*m.sin(theta) + Trace.shape[1]*p[1])
    #         # if out of range
    #         if xCord > Trace.shape[0]-1 or xCord < 0 or yCord > Trace.shape[1]-1 or yCord < 0:
    #             break
    #         if Trace[xCord, yCord] == 0: # if hit an edge
    #             break
        # if Trace[xCord,yCord] == 0:
            # break
    
    # respawn
    posInit = ((xCord-bordWidth)/pxl_mm[0], (yCord-bordWidth)/pxl_mm[1],0)
    # posInit = (p[0]*printArea[0], p[1]*printArea[1], 0)
    r.append(rover(posInit,step,L,pxl_mm,bordWidth,dMinMax,printArea)) # make an instance of the class

# make the border empty again. Then make the rover skirt the border by looking in front of it one pixel inside the border until it reaches an edge, then jumping to that point. Fix your respawn code too you dimwitted fool
f = plt.figure(1)
plt.imshow(np.transpose(Trace[:,-1:0:-1])) # flip to visually match image in
# note that the Y cords flip

g = plt.figure(2)
for x in range(len(r)-2):
    plt.plot(r[x].pos[:,0],r[x].pos[:,1],linewidth=.3,color=[0,0,0])
plt.plot(r[x+1].pos[:,0],r[x+1].pos[:,1],linewidth=.3)
plt.plot(r[x+2].pos[:,0],r[x+2].pos[:,1],linewidth=.3)



print(len(r))
plt.show()