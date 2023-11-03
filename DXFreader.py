from dfx_wrapper import read_dxf_fancy, file_dialog_dxf
import matplotlib.pyplot as plt

path = file_dialog_dxf()
pnts = read_dxf_fancy(path)  # reads dxf into data structure


# print(pnts)

# plt.figure(1)
plt.plot(pnts[:,0],pnts[:,1],'-o')

plt.show()
