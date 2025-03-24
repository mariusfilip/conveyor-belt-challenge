import argparse, random
import logging

from belt import Belt
from constants import FINISHED

DEFAULT_ITER_NUM: int = 100
DEFAULT_SIZE: int = 3

# Create the parser
parser = argparse.ArgumentParser(prog="python main.py",
                                 description="Simulation of a conveyor belt that assembles components into finished products. "
                                             "See ./README.md for full requirements.",
                                 epilog="If this program does not work, check README.md and also run main_t.py.")
parser.add_argument("-p", "--print", action="store_true", help="Pretty-print the belt and the workers at each tick.")
parser.add_argument("-o", "--offset", type=int, default=Belt.DEFAULT_OFFSET, help=f"Number of spaces to insert before each line in "
                                                                                               f"pretty-printing. Default is {Belt.DEFAULT_OFFSET}.")
parser.add_argument("-n", "--number", type=int, default=DEFAULT_ITER_NUM, help=f"Number of iterations to run the simulation for. Default is {DEFAULT_ITER_NUM}.")
parser.add_argument("-s", "--size", type=int, default=DEFAULT_SIZE, help=f"Size of the conveyor belt. Default is {DEFAULT_SIZE}.")
parser.add_argument("-r", "--rand", type=int, help="Fix the random seed for reproducibility.")
parser.add_argument("-f", "--fill", action="store_true", help="Whether to fill the belt with random components initially or not.")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode, printing INFO logging.")
parser.add_argument("-d", "--debug", action="store_true", help="Debug mode, printing DEBUG logging.")


# Parse the arguments
args = parser.parse_args()
print("Running the simulation with the following parameters:")
print(f"  Number of iterations            : {args.number}")
print(f"  Size of the conveyor belt       : {args.size}")
print(f"  Pretty-print the belt           : {args.print}")
print(f"  Offset for pretty-printing      : {args.offset}")
print(f"  Fill the belt initially         : {args.fill}")
print(f"  Verbose mode (log INFO level)   : {args.verbose}")
print(f"  Debug mode (log at DEBUG level) : {args.debug}")
print(f"  Random seed                     : {str(args.rand) if args.rand else 'generated by the system'}")

# Set logging
logging.basicConfig(level=logging.WARNING)
if args.verbose:
    logging.basicConfig(level=logging.INFO)
if args.debug:
    logging.basicConfig(level=logging.DEBUG)

# Fix random seed, if needed
if args.rand:
    random.seed(args.rand)

# Create the belt
b: Belt = Belt(args.size, pretty_print=args.print, offset=args.offset)

# Pre-fill the belt, if needed
if args.fill:
    b.pre_fill()

# Run the simulation
result, changes = b.work(args.number)
in_progress: dict[str, int] = b.get_in_progress()

# Print the results
print(f"\nNumber of finished products generated in {args.number} ticks: {result[FINISHED]}")
for c, n in result.items():
    if c != FINISHED:
        print(f"Number of '{c}' components untouched by any worker (generated or still on the belt): {n + in_progress[c]}")
print(f"Number of conveyor belt changes in {args.number} ticks: {changes}")
print("Done.")
