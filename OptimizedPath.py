import tkinter as tk
from tkinter import filedialog
import sys
import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import numpy as np
import matplotlib.pyplot as plt

plotterSize = [1979, 1000] # [x size, y size]

# Select a dxf File
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])

try:
    doc, auditor = recover.readfile(file_path)
except IOError:
    print(f'Not a DXF file or a generic I/O error.')
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')
    sys.exit(2)

# Get XY coordinates of DXF into an array
msp = doc.modelspace() # Get the modelspace entities
prevEnd = (-1,-1) # initiate previous x end point
coords = np.zeros((len(msp),2)) # initiate list of xy coordinates
pts = np.zeros((len(msp),2)) # initiate list of starting locations
pts_count = 1 # starting locations counter. Set at 1 so that the first point can be set manually
L = list() #initiate list
ii = 0 # counter
for entity in msp:
    # check if the entity is a line or a polyline
    if entity.dxftype() == 'LINE' or entity.dxftype() == 'LWPOLYLINE':        
        
        if prevEnd != entity.dxf.start and prevEnd != (-1,-1): # if new closed loop is starting and its not the first loop through
            L.append(coords[0:ii,:]) # add the previous closed loop to the list
            pts[pts_count,:] = coords[0,:] # save first coordinate of closed loop

            # reset
            coords = np.zeros((len(msp),2)) # reset list of xy coordinates
            ii = 0 # reset index counter
            pts_count = pts_count + 1 # starting cord counter

        coords[ii,0] = entity.dxf.start[0] # starting x coord of line
        coords[ii,1] = entity.dxf.start[1] # starting y coord of line

        prevEnd = entity.dxf.end # save end point of the last line for next loop itteration
        ii = ii + 1 # itterate counter
pts = pts[0:pts_count+1,:] # get rid of extra entries
pts[0,:] = [0,plotterSize[1]] # set starting point
#pts[-1,:] = [0,plotterSize[0]] # set end point

# plotting the points
#print(L[0])

# Calculates the Distance matrix from set of points in pts
D = np.sqrt(np.sum((pts[None, :] - pts[:, None])**2, -1))
print(pts)




# function to show the plot
for c in L:
    plt.plot(c[:,0], c[:,1])


plt.show()


       