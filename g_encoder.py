
# [
#     (color: red, [(0,1), (2, 0)]),
#     (color: blue, [(2, 5), (4,6)])
# ]

FeedRate = 10000
drawAccel = 500  # acceleration
travelAccel = 1500
penDelay = 100  # time for pen to raise or lower (ms)
jerk = 1.0  # jerk


def g_encode(lines):
    instructions = []

    # definitions
    x_0 = 0
    y_0 = 0

    # G-code HEADER
    instructions.append("; HEADER")
    instructions.append("G0 F{FeedRate}")
    instructions.append(f"M205 X{jerk}\n")  # set x jerk
    instructions += liftPen()
    instructions += homePen()

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





# definitions
def liftPen(f):
    f.write(f"G4 P{penDelay}\nM280 P0 S100 G0 Z10 \n")


def lowerPen(f):
    f.write(f"G4 P{penDelay}\nM280 P0 S0 G0 Z0\n")


def homePen(f):
    f.write(f"G28\n")


# Get the modelspace entities
msp = doc.modelspace()


# travels without drawing
def travelMove(x, y):
    f.write(f"; TravelMove\n")
    f.write(f"M204 T{travelAccel}\n")  # change to travel acceleration
    liftPen(f)  # pen up
    f.write(f"G0 X{x:.3f} Y{y:.3f}\n")  # go to final position
    f.write(f"M204 T{drawAccel}\n")  # change back to draw acceleration
    lowerPen(f)  # pen down


def drawMove(x, y, xprev):
    # continue to next postiion
    f.write(f"G0 X{x:.3f} Y{y:.3f}\n")

