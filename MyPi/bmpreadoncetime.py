import argparse
import max30102

parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-a", "--amount", type=int, default=100,
                    help="Amount of collected data, default 100")
parser.add_argument("-m", "--sample", type=int, default=100,
                    help="samples per second count, {0}, default 1000".format(" ".join(list(map(str,max30102.SAMPLES_PER_SECOND_DIC.keys())))))
parser.add_argument("-v", "--average", type=int, default=4,
                    help="adjacent samples can be averaged and decimated on the chip by setting this register, {0}, default 4".format(" ".join(list(map(str,max30102.SAMPLES_AVG_PER_FIFO_DIC.keys())))))
parser.add_argument("-r", "--unreversal", action="store_false",
                    help="when with -r, calc peak interval, when without -r, calc valley interval")
parser.add_argument("-s", "--save", action="store_true",
                    help="save IR data")
args = parser.parse_args()


m = max30102.MAX30102(args.sample,args.average)
hr = m.get_bpm(amount = args.amount,save = args.save, reversal = args.reversal)
print(hr)
m.shutdown()
    