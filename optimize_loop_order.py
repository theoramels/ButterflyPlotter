import numpy as np

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
    # minPath = np.zeros(shape=(len(loops), len(loops)), dtype=int)
    minPath = []
    totalDist = np.zeros(len(loops))
    for ii in range(len(loops)):
        tup = travellingSalesmanProblem(D, ii)  # find min path
        minPath.append(tup[0])
        totalDist[ii] = tup[1]
        print(str(ii) + " out of " + str(len(loops)) + " starting points tried")
    idx = np.where(np.amin(totalDist) == totalDist)
    return minPath[idx[0][0]]

def optimize_loops(loops):
    min_path = tryEveryStartPoint(loops)

    sortedLoops = []
    for n in range(len(loops)):
        sortedLoops.append(loops[min_path[n]])

    return sortedLoops
