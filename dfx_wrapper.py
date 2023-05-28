import tkinter as tk
from tkinter import filedialog
import sys
import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

from pathlib import Path

def file_dialog_dxf():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(filetypes=[("DXF files", "*.dxf")])
    return Path(path)


# reads dxf into list of list of points
def read_dxf(path):
    try:
        doc, auditor = recover.readfile(path)
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
        if entity.dxftype() in {"LINE", "LWPOLYLINE"}:
            current_loop.append((entity.dxf.start[0], entity.dxf.start[1]))
            if (entity.dxf.end[0], entity.dxf.end[1]) == current_loop[0]:
                current_loop.append(
                    current_loop[0]
                )  # end were you started. Finish the loops
                loops.append(current_loop)  # add loop to list of loops
                current_loop = []  # reset variable
    return loops
