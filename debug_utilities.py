import matplotlib.pyplot as plt
import numpy as np

def dump_loops(loops):
    # function to show the plot
    for loop in loops:
        plt.plot([p[0] for p in loop], [p[1] for p in loop])

    # # plot results
    # pts = np.array([loop[0] for loop in loops])
    # pts = pts[5, :]
    # plt.plot(pts[:, 0], pts[:, 1])

def dump_loops_path(loops):
    path = [point for loop in loops for point in loop]
    plt.plot([p[0] for p in path], [p[1] for p in path])


def block_and_show():
    plt.show()