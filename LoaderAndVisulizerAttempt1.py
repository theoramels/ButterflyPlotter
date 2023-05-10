import ezdxf
import tkinter as tk
from tkinter import filedialog
import sys
import matplotlib.pyplot as plt
from ezdxf import recover
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

# Code Requests: Black and White Image to Gcode


# define some conversion parameters
scale = 1  # scale factor for converting DXF units to mm
FeedRate = 10000
DrawAccel = 500 # acceleration
TravelAccel = 10000
penDelay = 140  # time for pen to raise or lower (ms)
jerk = 1.0 # jerk
plotterSize = [1600, 900]

# Select a dxf File
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])

# Creates a output gcode file with the same name as the input file
def make_output_file():
    saveFileName = file_path.split("/")[-1].split(".")[0]
    saveFileName += ".gcode"
    return saveFileName

# Safe loading procedure for dxf:
try:
    doc, auditor = recover.readfile(file_path)
except IOError:
    print(f'Not a DXF file or a generic I/O error.')
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')
    sys.exit(2)

# Rendering the DXF
cm = 1/2.54
if not auditor.has_errors:
    fig = plt.figure(layout = 'none')
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax, adjust_figure= False)
    Frontend(ctx, out).draw_layout(doc.modelspace(), finalize=True)
    fig.set_figwidth(16)
    fig.set_figheight(9)
    plt.show()
    fig.savefig('your.png', dpi=100)

# definitions
def liftPen(f):f.write(f'G4 P{penDelay}\nM280 P0 S100 G0 Z10 \n')
def lowerPen(f):f.write(f'G4 P{penDelay}\nM280 P0 S0 G0 Z0\n')
def homePen(f):f.write(f'G28\n')

# Get the modelspace entities
msp = doc.modelspace()

# travels without drawing
def travelMove(x,y):
    f.write(f'; TravelMove\n')
    f.write(f'M204 T{travelAccel}\n') # change to travel acceleration
    liftPen(f) # pen up
    f.write(f'G0 X{x:.3f} Y{y:.3f}\n') # go to final position
    f.write(f'M204 T{drawAccel}\n') # change back to draw acceleration
    lowerPen(f) # pen down

def drawMove(x,y,):
    # continue to next postiion
    f.write(f'G0 X{x:.3f} Y{y:.3f}\n')

with open(make_output_file(), 'w') as f:
    
    # claer file
    f.truncate(0)

    # definitions
    x_0 = 0
    y_0 = 0 

    # G-code HEADER    
    f.write(f'; HEADER\n')
    f.write(f'G0 F{FeedRate}\n') # set feedrate
    f.write(f'M205 X{jerk}\n') # set x jerk
    liftPen(f)
    homePen(f)

    # G-code BODY
    f.write(f'; Body\n')
    # iterate through every entitiy in the DXF file
    for entity in msp:

        # check if the entity is a line or a polyline
        if entity.dxftype() == 'LINE' or entity.dxftype() == 'LWPOLYLINE':

            # get the start and end points of the line or polyline
            start = entity.dxf.start
            end = entity.dxf.end

            # convert the coordinates from DXF units to a scale and apply the scale factor
            x_1 = start[0] * scale
            y_1 = start[1] * scale
            x_2 = end[0] * scale
            y_2 = end[1] * scale
            if x_1 != x_0 or y_1 != y_0:
                # move to the start of the next element
                travelMove(x_1,y_1)
            # move to the end of the current element
            drawMove(x_2,y_2)
            
            # store previous end values
            x_0 = x_2
            y_0 = y_2


    # G-code FOOTER
    f.write(f'; FOOTER\n')
    liftPen(f)
    f.write(f'G0 X0\n') # Gets Y axis out of the way
    f.write(f'M84\n') # Disable Steppers
    f.write(f'M282\n') # dePowers Servo

