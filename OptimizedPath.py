import tkinter as tk
from tkinter import filedialog
import sys
import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import numpy as np
import matplotlib.pyplot as plt
from g_encoder import GEncoder


def make_output_file():
    saveFileName = file_path.split("/")[-1].split(".")[0]
    saveFileName += ".gcode"
    return saveFileName

# reads dxf into list of list of points
def read_dxf():
    # Select a dxf File
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])

    try:
        doc, auditor = recover.readfile(file_path)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")
        sys.exit(2)

    # Get XY coordinates of DXF into an array
    msp = doc.modelspace()  # Get the modelspace entities
    current_loop = []
    loops = []  # initiate list
    for entity in msp:
        # check if the entity is a line or a polyline
        if entity.dxftype() in {"LINE","LWPOLYLINE"}:

            current_loop.append((entity.dxf.start[0],entity.dxf.start[1]))
            if (entity.dxf.end[0], entity.dxf.end[1]) == current_loop[0]:
                loops.append(current_loop)
                current_loop = []
    return loops, file_path

# Zains implementation of traveling Salesman Problem
def travellingSalesmanProblem(D, start):
    # D : distance matrix. the first row will be treated as the starting node

    l = D.shape  # number of elements in one row of distance matrix
    visited = np.zeros(l[0]) == 1  # nodes visited in boolean array
    minPath = np.zeros(l[0], dtype=int)  # order of nodes visited
    maxDist = np.amax(D)  # find max distance between any two nodes
    totalDist = 0
    next = start  # next row
    visited[next] = True  # says the first node has already been visited
    minPath[0] = next  # record the first next node
    for ii in range(1, l[0]):
        D[next, visited] = maxDist + 1  # add current node to the exclusion list
        dist = np.amin(D[next, :])
        idx = np.where(dist == D[next, :])  # find the closest node
        next = idx[0][0]  # set that as the next node
        minPath[ii] = next  # record that thats the next node
        visited[minPath[ii]] = True  # check that node off the list
        totalDist = totalDist + dist

    return minPath, totalDist

# tries every starting location
def tryEveryStartPoint(loops):
    # grabs starting points of each loop into a list
    pts = np.array([loop[0] for loop in loops])

    # Calculates the Distance matrix from set of points in pts
    D = np.sqrt(np.sum((pts[None, :] - pts[:, None]) ** 2, -1))

    # try starting from every closed loop and pick the best starting point
    minPath = np.zeros(shape=(len(loops), len(loops)), dtype=int)
    totalDist = np.zeros(len(loops))
    for ii in range(len(loops)):
        tup = travellingSalesmanProblem(D, ii)  # find min path
        minPath[:, ii] = tup[0]
        totalDist[ii] = tup[1]
        print(str(ii) + " out of " + str(len(loops)) + " starting points tried")
    idx = np.where(np.amin(totalDist) == totalDist)
    minPath = minPath[:, idx[0][0]]
    return minPath


loops, file_path = read_dxf() # reads dxf into data structure

minPath = tryEveryStartPoint(loops) # optimizes path

# function to show the plot
for loop in loops:
    plt.plot([p[0] for p in loop], [p[1] for p in loop])

pts = np.array([loop[0] for loop in loops])
pts = pts[minPath,:]
plt.plot(pts[:,0] , pts[:,1])
#plt.show()

with open(make_output_file(), "w") as f:
    encoder = GEncoder()
    encoder.encode(loops,f)
