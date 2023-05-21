from collections import namedtuple

Path = namedtuple('Path', ['tool', 'points'])
Point = namedtuple('Point', ['x', 'y'])


# [
#     (color: red, [(0,1), (2, 0)]),
#     (color: blue, [(2, 5), (4,6)])
# ]

FeedRate = 10000
drawAccel = 500  # acceleration
travelAccel = 1500
penDelay = 100  # time for pen to raise or lower (ms)
jerk = 1.0  # jerk


# definitions
liftPen = [f"G4 P{penDelay}", "M280 P0 S100 G0 Z10"]
lowerPen = [f"G4 P{penDelay}", "M280 P0 S0 G0 Z0"]
homePen = ["G28"]


def g_encode(lines):
    instructions = []

    # definitions
    x_0 = 0
    y_0 = 0

    # G-code HEADER
    instructions += ["; HEADER", "G0 F{FeedRate}", f"M205 X{jerk}", *liftPen, *homePen]

    # G-code BODY
    f.write(f"; Body\n")
    # iterate through every entitiy in the DXF file
    for locList in L[minPath]:
        for coords in locList:
            print(coords)
            # drawMove(coords[0],coords[1])

    # G-code FOOTER
    f.write(f"; FOOTER\n")
    liftPen(f)
    f.write(f"G0 X0\n")  # Gets Y axis out of the way
    f.write(f"M84\n")  # Disable Steppers
    f.write(f"M282\n")  # dePowers Servo


# travels without drawing
def travelMove(x, y):
    return [
        "; TravelMove",
        f"M204 T{travelAccel}",
        *liftPen,
        f"G0 X{x:.3f} Y{y:.3f}",
        f"M204 T{drawAccel}",
        *lowerPen,
    ]


def drawMove(x, y):
    return [f"G0 X{x:.3f} Y{y:.3f}"]
