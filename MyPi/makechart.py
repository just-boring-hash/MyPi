import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="make chart, data from MAX30102")
parser.add_argument("-f", "--file", type=str, default=None,
                    help="data file name")
parser.add_argument("-w", "--width", type=int, default=700,
                    help="show chart y width by Avg.")
args = parser.parse_args()

fig = plt.figure()
with open("./{0}".format(args.file), "r") as f:
    hr = f.readline()
    peaks = f.readline().split(",")
    peakinv = f.readline().split(",")
    ir = f.readline().split(",")
    ir = list(map(int,ir))
    peaks = list(map(int,peaks))
ax = fig.add_subplot(111)

ax.plot(np.arange(len(ir)), ir, c="orange", label="IR")
avg = np.mean(np.array(ir))
plt.title(hr)
plt.plot(np.array(peaks),np.array([ir[peaks[i]] for i in range(0,len(peaks))]), 'o')
ax.set_ylim(avg - args.width, avg + args.width)
plt.show()