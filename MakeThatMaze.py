# Import the necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import cv2
import math as m
import random
from scipy import signal

# next thing to do is figure out how to stamp the thing delayed so that it doesn't interfere with the sensors you dim wit

dMinMax = (1,10) # (mm) min and max distance between lines
printArea = (500,550) # (x,y) in mm
pxlPerSqmm = 100 # pixels per square mm
fname = 'test2.jpg' # input image file name
L= 2000 # max itterations

# pre generate list of circles to use later
def CircleGenerator(dMinMax,pxlPerSqmm):
    sz = m.ceil(dMinMax[1]*m.sqrt(pxlPerSqmm))+1 # the +1 stopped out of bounds errors happening idx why
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

# pre generate a list of circles to use later
c = CircleGenerator(dMinMax,pxlPerSqmm)

# circle test code
# d = 0.5 # radius of circle in mm
# tmp = m.floor(d*m.sqrt(pxlPerSqmm)) # converts to pixles
# plt.imshow(c[tmp]) # displays as image
# print(c[tmp].shape)
           

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




curPxlPerSqmm = (A.shape[0]*A.shape[1])/(printArea[0]*printArea[1])


upScale = m.ceil(pxlPerSqmm/curPxlPerSqmm)

A = cv2.resize(A, (0, 0), fx=upScale, fy=upScale)

filt = gkern(upScale*5,upScale*2.5) # blur filter
A = signal.convolve(A,filt,mode='same') # blur

# print(A.shape)
# print(printArea[0]*scf) # how to scale the print area coords to the image pxl coords
# print(printArea[1]*scf) # ^^^^^

class rover:
    def __init__(self, initialPosition,step,L,TraceScf):
        self.step = step # step size (mm)
        self.scf = TraceScf
        # self.pos = [x,y,theta]
        self.pos = np.zeros((L+1,3))*-1 # initiate position array for speed
        self.pos[0,:] = np.array(initialPosition) # assign initial position
        self.n = 0 #counter to keep track of where in the position array we are

    def move(self,d): # d : distance from other lines
        rotation = .1 # change this to depend on Trace image darkness

        theta = self.pos[self.n,2] + rotation # change theta
        x = self.pos[self.n,0] + m.cos(theta)*self.step # calc new x position
        y = self.pos[self.n,1] + m.sin(theta)*self.step # calc new y position
        newPos = np.array((x,y,theta))

        self.n = self.n+1 # increment in array
        self.pos[self.n,:] = newPos # save new position

    def stamp(self,d,Trace,c): # distance from other lines
        curPos = np.round(self.pos[self.n,:]*self.scf) # convert from mm to pxls
        curPos = curPos.astype(int)
        
        radius = m.floor(d*self.scf) # converts to pixles
        width = round((c[radius].shape[0]-1)/2)
        rows = (curPos[0]-width, curPos[0]+width+1)
        cols = (curPos[1]-width, curPos[1]+width+1)
        mask = np.logical_or(Trace[rows[0]:rows[1], cols[0]:cols[1]], c[radius])
        Trace[rows[0]:rows[1], cols[0]:cols[1]] = mask



TraceScf = m.sqrt(pxlPerSqmm)
TraceSize = round(printArea[0]*TraceScf),round(printArea[1]*TraceScf)
Trace = np.zeros(TraceSize)
print(TraceSize)

posInit = (50,50,m.pi)
step = 1
r = rover(posInit,step,L,TraceScf) # make an instance of the class
for n in range(L):
     d = 1 # distance from other lines. Sample image to get this value and scale it however you like
     r.move(d)
     r.stamp(d,Trace,c)


plt.imshow(Trace)

# plt.plot(r.pos[:,0],r.pos[:,1],marker='o',linewidth=.2,color=[0,0,0])
plt.show()

