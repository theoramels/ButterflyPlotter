# Import the necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import cv2
import math as mth

maxPrintArea = np.array([200, 270]) # (Y, X) in mm
L= 50000
t = .1

All = np.load('Gradient.npy')
A =      All[:,:,0]
Ahorz =  All[:,:,1]
Avert =  All[:,:,2]
Atheta = All[:,:,3]
Amag =   All[:,:,4]




imgAR = A.shape[0]/A.shape[1]
printAR = maxPrintArea[0]/maxPrintArea[1]
if imgAR > printAR:
    # line up horizontal side
    printArea = (maxPrintArea[0], maxPrintArea[0]/imgAR)
else: # if tall and skinny
    printArea = (maxPrintArea[1]*imgAR, maxPrintArea[1])

printArea = (printArea[1],printArea[0]) # switch to (x,y) format



class marble:
    def __init__(self, mass, timeStep, velocity, position, loopLength,printArea):
        self.t = timeStep
        self.mass = mass
        self.vel = velocity
        self.pos = np.ones((loopLength+1,2))*-1 # initiate position array for speed
        self.pos[0,:] = np.array(position) # assign initial position
        self.n = 0 #counter to keep track of where in the array we are
        self.curPos = np.array(position) # initiates current position
        self.printArea = printArea
        self.done = 0 # flag to determine when marble has rolled out of bounds
    def role(self, a):
        # move marble to new position
        posx = self.pos[self.n,0] + self.vel[0]*self.t # x component
        posy = self.pos[self.n,1] + self.vel[1]*self.t # y component
        newPos = np.array((posx,posy)) # new position
        if self.done == 0: # if the marble is still in bounds
            # if point is within bounds
            if (newPos[0] >= 0) and (newPos[1] >= 0) and (newPos[0] <= self.printArea[0]) and (newPos[1] <= self.printArea[1]):
                self.pos[n+1,:] = newPos  # assigns new position to position array
                self.curPos = self.pos[self.n,:] # update current position
                # calculate new velocity based on acceleration given to marble at its new location
                velx = self.vel[0] + (a[0]/self.mass)*self.t # x component
                vely = self.vel[1] + (a[1]/self.mass)*self.t # y component
                self.vel = (velx,vely) # update with new velocity
                self.n = self.n + 1 # bump counter up
            else:
                self.pos = self.pos[self.pos[:,0] != -1]
                self.done = 1

print(printArea)
print(A.shape)
m = []
vi = (0,.1) # initial (x,y) velocity
xi = (100,100) # initial (x,y) position
m.append(marble(1,t,vi,xi,L,printArea))


scl = A.shape[1]/printArea[0]
print(scl)
for n in range(L):
    curPos = m[0].curPos
    scaledIdx = (round(curPos[0]*scl),round(curPos[1]*scl))
   
    ax = Ahorz[scaledIdx[1],scaledIdx[0]]
    ay = Avert[scaledIdx[1],scaledIdx[0]]
    a = (ax,ay)
    m[0].role(a)  
    


plt.plot(m[0].pos[:,0],m[0].pos[:,1])#,marker='o')
plt.show()

output = A
output = output+np.amin(output)
output = np.round((output/np.amax(output))*255)
cv2.imwrite('testProcessed.png',output)