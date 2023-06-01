from g_encoder import GEncoder
from optimize_loop_order import optimize_loops
from dfx_wrapper import read_dxf, file_dialog_dxf
import matplotlib.pyplot as plt

path = file_dialog_dxf()
loops = read_dxf(path)  # reads dxf into data structure





plt.scatter(loops[1])
plt.show()