from max30102_calc import calc_ir
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-d", "--debug", action="store_true",
                    help="debug mode, when without pi")
parser.add_argument("-a", "--amount", type=int, default=100,
                    help="Amount of collected data, default 100")
parser.add_argument("-r", "--reversal", action="store_false",
                    help="when with -r, calc peak interval, when without -r, calc valley interval")
parser.add_argument("-s", "--save", action="store_true",
                    help="save IR data")
args = parser.parse_args()


if args.debug:
    ir = []
    with open("./ir.log", "r") as f:
        for r in f:
            ir.append(int(r))

    red = []
    with open("./red.log", "r") as f:
        for r in f:
            red.append(int(r))
else:
    import max30102
    m = max30102.MAX30102()
    red, ir = m.read_sequential(args.amount)

hr,peaks,peakinv = calc_ir(ir, reversal = args.reversal)

if args.save:
    with open("./irdata_{0}_{1}.csv".format(datetime.now().strftime("%Y%m%d%H%M%S"),int(hr)), "w") as f:
        f.write(str(hr) + "\n")
        f.write((",").join(map(str,peaks)))
        f.write("\n")       
        f.write((",").join(map(str,peakinv)))
        f.write("\n")       
        f.write((",").join(map(str,ir)))

if not args.debug:
    m.shutdown()