from g_encoder import GEncoder
from optimize_loop_order import optimize_loops
import debug_utilities
from dfx_wrapper import read_dxf, file_dialog_dxf

path = file_dialog_dxf()
loops = read_dxf(path)  # reads dxf into data structure

debug_utilities.dump_loops_path(loops)

sortedLoops = optimize_loops(loops)  # finds a good path through loops

debug_utilities.dump_loops_path(sortedLoops)

outfile = path.with_suffix(".gcode")

encoder = GEncoder()
with open(outfile, "w") as f:
    encoder.encode(sortedLoops, f)

print('Done')
debug_utilities.block_and_show()
