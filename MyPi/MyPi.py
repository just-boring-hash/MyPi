from max30102_calc import calc_ir
import argparse

parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-d", "--debug", action="store_true",
                    help="debug mode, when without pi")
parser.add_argument("-a", "--amount", type=int, default=100,
                    help="Amount of collected data, default 100")
parser.add_argument("-r", "--reversal", action="store_false",
                    help="when with -r, calc peak interval, when without -r, calc valley interval")
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
    red, ir = m.read_sequential(args.time)

print(calc_ir(ir, reversal = args.reversal))

if not args.debug:
    m.shutdown()