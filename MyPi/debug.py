from max30102 import calc_ir
import argparse
from datetime import datetime

ir = []
with open("./ir.log", "r") as f:
    for r in f:
        ir.append(int(r))

red = []
with open("./red.log", "r") as f:
    for r in f:
        red.append(int(r))

hr,peaks,peakinv = calc_ir(ir, reversal = True)

if True:
    with open("./irdata_{0}_{1}.csv".format(datetime.now().strftime("%Y%m%d%H%M%S"),int(hr)), "w") as f:
        f.write(str(hr) + "\n")
        f.write((",").join(map(str,peaks)))
        f.write("\n")       
        f.write((",").join(map(str,peakinv)))
        f.write("\n")       
        f.write((",").join(map(str,ir)))
