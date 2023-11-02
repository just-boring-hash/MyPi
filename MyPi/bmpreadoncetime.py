import argparse
import max30102

parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-a", "--amount", type=int, default=100,
                    help="Amount of collected data, default 100")
parser.add_argument("-r", "--unreversal", action="store_false",
                    help="when with -r, calc peak interval, when without -r, calc valley interval")
parser.add_argument("-s", "--save", action="store_true",
                    help="save IR data")
args = parser.parse_args()


m = max30102.MAX30102()
print("init max30102 ok")
hr = m.get_bpm(amount = args.amount,save = args.save, reversal = args.reversal)
print(hr)
m.shutdown()
    