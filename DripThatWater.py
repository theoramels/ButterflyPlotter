# Import the necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import cv2
import math as mth
import random



L= 2000

All = np.load('Gradient.npy')
A =      All[:,:,0]
Ahorz =  All[:,:,1]
Avert =  All[:,:,2]
Atheta = All[:,:,3]
Amag =   All[:,:,4]


def myDist(vector1,vector2):
    dist = [(a - b)**2 for a, b in zip(vector1, vector2)]
    dist = mth.sqrt(sum(dist))
    return dist



class marble:
    def __init__(self, position, loopLength,printArea):
        self.pos = np.ones((loopLength+1,2))*-1 # initiate position array for speed
        self.pos[0,:] = np.array(position) # assign initial position
        self.n = 0 #counter to keep track of where in the array we are

        self.curPos = np.array(position) # initiates current position
        self.printArea = printArea # bounds

        self.filtLen = 50 # moving average length
        self.mvAvg = np.zeros((loopLength+self.filtLen,1)) # keeps track of the speed of the marble
        self.mvAvg[:self.filtLen] = 1 # initiate with ones to avoid triggering done condition

        self.done = 0 # flag to determine when water is done rollin

    def slide(self,a):
         # check if marble has stopped rolling
        self.mvAvg[n+self.filtLen] = abs(a[0]) + abs(a[1])
        avgAcl = np.sum(self.mvAvg[n:(n+self.filtLen)])/self.filtLen
        # print(avgAcl)
        if avgAcl < 0.0005:
            self.done = 1
        
        if self.done == 0: 
            step = .01 # length of step to take every iteration units: (% of image)

            dist = mth.sqrt(a[0]**2 + a[1]**2) # distance to move the marble
            # move marble to new position
            posx = self.pos[self.n,0] + (a[0]/dist)*step # x component 
            posy = self.pos[self.n,1] + (a[1]/dist)*step # y component
            newPos = np.array((posx,posy)) # new position

            # if the marble is still in bounds
            if (newPos[0] >= 0) and (newPos[1] >= 0) and (newPos[0] <= self.printArea[0]) and (newPos[1] <= self.printArea[1]):

                # if marble is still goin
                self.pos[n+1,:] = newPos  # assigns new position to position array
                self.curPos = self.pos[self.n,:] # update current position
                
                self.n = self.n + 1 # bump counter up
            else:
                self.done = 1
        else:
            self.pos = self.pos[self.pos[:,0] != -1,:]

    def returnTest(self):
        return 'penis'


# scale print area from 0 - 100
printArea = np.array(A.shape) # print Area in %% (x,y)
printArea = (printArea/np.amax(printArea))*100

# initiate the marbles
rng = np.random.default_rng()



m = []
sclx = (A.shape[1]-1)/printArea[0]
scly = (A.shape[0]-1)/printArea[1]

N = 500 # number of samples to take
xi = np.linspace(1,printArea[0]-1,N)
yi = np.linspace(1,printArea[1]-1,N)
for x in range(len(yi)):
    for y in range(len(xi)):
        scaledIdx = (round(xi[x]*sclx),round(yi[y]*scly))
        
        pxl = A[scaledIdx[1],scaledIdx[0]]
        if pxl < mth.pow(rng.random(),4):
            m.append(marble((xi[x],yi[y]),L,printArea))



done = []
slope = np.zeros((L,2))
for M in range(len(m)):
    print('Marble Number: ' + str(M) + '/' + str(len(m)))

    for n in range(L):
        # if m[M].done == 0: # if marble is still rolling
        curPos = m[M].curPos
        scaledIdx = (round(curPos[0]*sclx),round(curPos[1]*scly))
            
        # sample image to get slope
        ax = Ahorz[scaledIdx[1],scaledIdx[0]]
        ay = Avert[scaledIdx[1],scaledIdx[0]]
        a = (ax,ay)
        slope[n,0] = ax
        slope[n,1] = ay
            
        m[M].slide(a)
        done.append(m[M].done)
    plt.plot(m[M].pos[:,0],m[M].pos[:,1],linewidth=.2,color=[0,0,0])

# plt.plot(m[0].pos[:,0],marker='o')
# plt.plot(m[0].pos[:,1],marker='o')

# plt.plot(slope[:,0],marker='o')
# plt.plot(slope[:,1],marker='o')
# plt.plot(done)
# plt.plot(m[0].pos[:,0]+m[0].pos[:,1],marker='o')
plt.show()





output = A
output = output+np.amin(output)
output = np.round((output/np.amax(output))*255)
cv2.imwrite('testProcessed.png',output)

# when you eventually sample the water droplet lines, make sure to undersample them,
# you definetily don't need precision more than 0.1 mm for this but the algorithm needs
# more than that in order to detect endpoints.
# so over sample for now for the sake of smooth lines, then undersample them later
# undersample them smart like: calucate the distance between each point and the next, 
# then use that distance to determine weather to keep it or not since the points 
# aren't evenly spaced at all. 