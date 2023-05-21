import ezdxf

# Define some conversion parameters
scale = 0.5  # scale factor for converting DXF units to mm
feedrate = 2500  # feedrate in mm/min

# Open the DXF file
doc = ezdxf.readfile("RobotMaze.dxf")


# definitions
def liftPen(f):
    f.write(f"M280 P0 S100 G0 Z10 \n")


def lowerPen(f):
    f.write(f"M280 P0 S0 G0 Z0\n")


def homePen(f):
    f.write(f"G28\n")


# Get the modelspace entities
msp = doc.modelspace()


# travels without drawing
def travelMove(x, y):
    f.write(f"; TravelMove\n")
    f.write(f"G4 P300\n")
    liftPen(f)
    # go to final position
    f.write(f"G1 X{x:.3f} Y{y:.3f}\n")
    f.write(f"G4 P300\n")
    lowerPen(f)


def drawMove(
    x,
    y,
):
    # continue to next postiion
    f.write(f"G1 X{x:.3f} Y{y:.3f}\n")


with open("output.gcode", "w") as f:
    # claer file
    f.truncate(0)
    # set feed
    f.write(f"G1 F{feedrate}\n")
    # definitions
    x_0 = 0
    y_0 = 0
    # HEADER
    f.write(f"; HEADER\n")
    liftPen(f)
    homePen(f)

    # BODY
    f.write(f"; Body\n")
    # iterate through every entitiy in the DXF file
    for entity in msp:
        # Check if the entity is a line or a polyline
        if entity.dxftype() == "LINE" or entity.dxftype() == "LWPOLYLINE":
            # Get the start and end points of the line or polyline
            start = entity.dxf.start
            end = entity.dxf.end

            # Convert the coordinates from DXF units to a scale and apply the scale factor

            x_1 = start[0] * scale
            y_1 = start[1] * scale
            x_2 = end[0] * scale
            y_2 = end[1] * scale
            if x_1 != x_0 or y_1 != y_0:
                travelMove(x_1, y_1)
            drawMove(x_2, y_2)

            # store previous end values
            x_0 = x_2
            y_0 = y_2

    # RESET
    f.write(f"; RESET\n")
    f.write(f"G0 X0\n")
    f.write(f"M280 P0 S100\n")
