import numpy as np
from matplotlib import pyplot as plt


triangle_grid = np.array([[1, 0],
                       [0.5, np.sqrt(0.75)]])


def rotate(theta, points):
    rot_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                       [np.sin(theta), np.cos(theta)]])
    return points @ rot_matrix


def debug_plot(points):
    x, y = points.T
    plt.plot(x,y)
    plt.show()


class SpaceFillingCurve:
    segment_dirs = None
    unit_points = None
    natural_end = None

    def __init__(self, segment_values, triangle=False) -> None:
        segment_values = np.array(segment_values)
        self.segment_dirs = segment_values[:, 2:]
        self.unit_points = self.get_unit_points(segment_values[:, :2], triangle)

    def get_unit_points(self, steps, triangle):
        points = np.empty((len(steps) + 1, 2))
        points[0] = [0, 0]

        for i, step in enumerate(steps):
            pos = points[i]
            new_point = pos + step
            points[i + 1] = new_point

        if triangle:
            points = points @ triangle_grid

        self.natural_end = points[-1]

        length = np.linalg.norm(points[-1] - points[0])
        points = points / length
        angle = np.arctan2(points[-1][1], points[-1][0])
        points = rotate(angle, points)

        assert(np.allclose(points[0], [0,0]))
        assert(np.allclose(points[-1], [1,0]))

        return points

    def get_points(self, iterations: int):
        return self.get_points_rec(np.array([0,0]), self.natural_end, np.array([1,1]), iterations)

    def get_points_rec(self, start, end, segment, iterations_left):
        if iterations_left == 0:
            return np.array([start, end])

        points = None

        step_points = self.perform_step(start, end, segment)
        for i, seg in enumerate(self.segment_dirs[::segment[0]]):
            new_points = self.get_points_rec(step_points[i], step_points[i+1], seg * segment, iterations_left - 1)
            if points is None:
                points = new_points
            else:
                points = np.append(points, new_points, axis=0)

        return points

    def perform_step(self, start, end, segment):
        points = self.unit_points
        if segment[1] == -1:
            points = points * [1,-1]
        if segment[0] == -1:
            points = np.flipud(points * [-1,1] + [1,0])

        assert(np.allclose(points[0], [0,0]))
        assert(np.allclose(points[-1], [1,0]))

        norm = end - start
        points = points * np.linalg.norm(norm)
        angle = np.arctan2(norm[1], norm[0])
        points = rotate(-angle, points)
        points = points + start

        assert(np.allclose(points[0], start))
        assert(np.allclose(points[-1], end))

        return points



Polya_Sweep = SpaceFillingCurve([
    [1,0,1,-1],
    [0,1,-1,1]
])

p = Polya_Sweep.get_points(12)
debug_plot(p)

# test
Gosper_Curve = SpaceFillingCurve([
    [1,0,1,1],
    [0,1,-1,-1],
    [-1,0,-1,-1],
    [-1,1,1,1],
    [1,0,1,1],
    [1,0,1,1],
    [1,-1,-1,-1]
], triangle=True)

p = Gosper_Curve.get_points(5)
debug_plot(p)