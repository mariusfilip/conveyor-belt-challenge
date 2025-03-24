# conveyor-belt-challenge
Challenge for the position of Software Engineering Manager with the **Raspberry Pi Foundation**.

## Problem Statement

### Overview
There is a factory production line around a single conveyor belt.

Components (of type A and B) come onto the start of the belt at random intervals; workers must take one component of each type from the belt as they come past, and combine them to make a finished product C.

The belt is divided into fixed-size slots; each slot can hold only one component or one finished product.  There are a number of worker stations on either side of the belt, spaced to match the size of the slots on the belt, like this:

![Conveyor Belt](conveyor-belt.png)

In each unit of time, the belt moves forwards one position, and there is time for a worker on one side of each slot to either take an item from the slot or replace an item onto the belt. The worker opposite can't touch the same belt slot while they do this. (So you can't have one worker picking something from a slot while their counterpart puts something down in the same place). 

Once a worker has collected one of both types of component, they can begin assembling the finished product. This takes an amount of time, so they will only be ready to place the assembled product back on the belt on the fourth subsequent slot. While they are assembling the product, they can't touch the conveyor belt. Workers can only hold two items (component or product) at a time; one in each hand.

### Task
Create a simulation of this, with three pairs of workers. At each time interval, the slot at the start of the conveyor belt should have an equal (1/3) chance of containing nothing, a component A or a component B.

Run the simulation for 100 steps, and compute how many finished products come off the production line, and how many components of each type go through the production line without being picked up by any workers.

## Submitting your task 
Once you have completed your simulation, submit your source code, any documentation and sample output by replying to the email sent to you with this document.

Feel free to use Generative AI and other assistive technologies in developing your answer. Please be transparent about the tools you used in your submission by including a clear overview of what tools you used and how. Be ready to explain every aspect of the code you submit.  

Submission deadline is 24 hours before your interview.

### Hints and Tips 
- You should expect to spend no more than two or three hours on this challenge. 
- The code does not have to be 'production quality', but we will be looking for evidence that it's written to be somewhat extensible, and that a third party would be able to read and maintain it. 
- Be sure to state your assumptions. 
- During the interview, we may ask about the effect of changing certain aspects of the simulation. (E.g. the length of the conveyor belt.) 
- Flexibility in the solution is preferred, but we are also looking for a sensible decision on where this adds too much complexity. (Where would it be better to rewrite the code for a different scenario, rather than spending much more than the allotted time creating an overly complicated, but very flexible simulation engine?) 
- Don’t hesitate to ask questions. 
- Be mindful that the evaluators may be on Linux, OSX or Windows. Please avoid using platform-specific APIs and clearly document limitations on how your code can be run.

## Implementation

The solution exists in a dedicated [GitHub repository](https://github.com/mariusfilip/conveyor-belt-challenge). Running it requires Python 3.13.2 or later.

> [!WARNING]
> 
> It is strongly recommended to install `virtualenv` and `pip` to create a virtual environment and install the required dependencies: 
> ```bash
> 
> git clone https://github.com/mariusfilip/conveyor-belt-challenge
> pushd conveyor-belt-challenge
> pip install virtualenv
> virtualenv .venv
> .venv/bin/activate
> pip install -r requirements.txt
> ```

In order to leave the virtual environment, run: `deactivate`.

## Running

The most direct way to run the program is from the command line:

```bash
python main.py
```

> **Important:** it is _highly_ recommended to create a virtual environment and run it from within the virtual environment. The current form of the program does not support packaging as an executable.

### Help

The application supports customisation via command line parameters. Run `python main.py -h` for help:

```bash
usage: Conveyor Belt Challenge [-h] [-p] [-o OFFSET] [-n NUMBER] [-s SIZE] [-r RAND] [-f] [-v] [-d]

Simulation of a conveyor belt that assembles components into finished products. See ./README.md for full requirements.

options:
  -h, --help           show this help message and exit
  -p, --print          Pretty-print the belt and the workers at each tick.
  -o, --offset OFFSET  Number of spaces to insert before each line in pretty-printing. Default is 2.
  -n, --number NUMBER  Number of iterations to run the simulation for. Default is 100.
  -s, --size SIZE      Size of the conveyor belt. Default is 3.
  -r, --rand RAND      Fix the random seed for reproducibility.
  -f, --fill           Whether to fill the belt with random components initially or not.
  -v, --verbose        Verbose mode, printing INFO logging.
  -d, --debug          Debug mode, printing DEBUG logging.

If this program does not work, check README.md and also run main_t.py.
```

### Output

The application supports pretty-printing of the program's state via the `-p` argument. This parameter makes the application print the initial state and then the evolving state with each tick.

Each tick printing has the format:

```
Tick <n>                                        # <n> = tick's ordinal number
--------

Inserted: <component or 'nothing'>
  | <worker status> | ... | <worker status> |   # absent if all workers empty-handed
  +++++++++++++++++++++++++++++++++++++++++++
  | <slot content>  | ... | <slot content>  | <-- content of the conveyor belt
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  | <worker status> | ... | <worker status> |   # absent if all workers empty-handed
Generated: <component or finished product or 'nothing'>
```

A worker above the conveyor belt is represented vertically as follows:

```
<left hand>,<right hand>     # an empty hand is represented by a whitespace
<assembly ticks remaining>   # if the worker is assembling a product, otherwise absent
```

> Workers above the conveyor belt are printed also vertically, but in reverse order: ticks remaining on top (if present)

#### Examples

```
Tick 3
------

Inserted: nothing
  +++++++++++++++++++
  |     |     |     |
  ~~~~~~~~~~~~~~~~~~~
  | B,  |     |     |
Generated: nothing
```

In this tick, all the upper workers are empty-handed. The belt is empty and the first lower worker has its right hand empty. The tick inserted an empty slot and ejected an empty slot.

```
Tick 5
------

Inserted: B
  | B,  |     |     |
  +++++++++++++++++++
  |     |     |     |
  ~~~~~~~~~~~~~~~~~~~
  | 3   |     |     |
  | B,A |     |     |
Generated: nothing

=====================

Tick 6
------

Inserted: A
  | B,A |     |     |
  | 4   |     |     |
  +++++++++++++++++++
  |     |     |     |
  ~~~~~~~~~~~~~~~~~~~
  | 2   |     |     |
  | B,A |     |     |
Generated: nothing
```

In `Tick 5` here the belt received component `B` which was consumed by the first upper worker. `Tick 6` injected component `A` which the same worker consumed and started assembling a new product. During this time, the first lower worker advanced two steps into assembling their own product.

## Initial State and Execution Control

By default, the simulation starts with an empty conveyor belt. The `f` argument changes that, in the sense that the belt gets prepopulated at random before the simulation starts. Using the `-p` argument makes the application display the initial state.

By default, the simulation runs randomly. Randomization can be controlled by providing a random seed with the `-r` argument. The seed may not be 0.

The user may vary the size of the conveyor belt (and the number of workers as a result, see the `-s` argument), or the number of iterations that the program will execute (see the `-n` argument). In combination with `-p` and `-r` they provide a great way to test the program manually.

### Unit testing

The application is unit tested. Run `python main_t.py` to run all the tests.

## Assumptions
- **Synchronous execution:** the whole simulation is governed by ticks, withing a tick the order of operations being:
  - shift the conveyour belt
  - insert a component (or nothing) at the front of the belt, all options with equal chances
  - make each worker operate upon the conveyor belt (if possible) in order of priorities (see below)
- **Holding allowed:** if a worker has finished a product but their slot isn't empty, then the worker is allowed to hold the product (by convention, in the right hand) in order to wait for an empty slot
- **Swapping finished products allowed:** if a worker is holding a finished product yet its slot isn't empty, then the worker may swap the finished product with the one on the belt (under some conditions). This behaviour is allowed in order to reduce the waiting time until placing a finished product on the belt
- **Swapping duplicates allowed:**: if a worker ends up with the same component in both hands, they are allowed to swap one of them with the component on the belt (under some conditions)
- **Prioritized order of execution:** within a tick, all the workers try to operate upon their respective slots (if possible) after the belt is shifted and the first slot is randomly filled in. The order in which workers perform is determined as follows:
  - all the worker pairs get randomized, the workers within each pair get randomized
  - the workers are considered in the reverse order of _priority number_
  - priority numbers are values calculated by `Worker.priority` that strongly favour completion of product assembly at the expense of levelling the work throughout the worker set
    > It is safe to say that the application is _greedy_ when it comes to completing any product assembly that is in progress
  - the priority number of a worker _pair_ is the product of worker priorities. This strongly favours workers with higher priotity number
- **Component-in-progress inclusion:** the application also counts the components (untouched by any worker) that are _still on the conveyor belt_ when the program stops. For example, if the belt ejected 3 components of type `A`, 2 being untouched and 1 touched and on the belt there are 2 components `A`, one of them touched by a worker, then the application will report 2+1 = 3 for components of type `A`
- **Product-in-progress exclusion:** the application counts only the finished products `C` that have left the conveyor belt. Those still on the belt are ignore when reporting the number of finished products. The touched/untouched counting does not matter for finished product

## Design Considerations
There are three essential classes within this application:
- `Worker` models a worker. It is a state machine that advances with each tick
- `WorkerPair` models a slot on the conveyor belt surrounded by the two workers. It controls the order of execution between the two workers
- `Belt` models the whole conveyor belt and its workers. It controls the injection of new components onto the belt, the order of workers to execute, as well as printing the state (if chosen by the user)

### Exensibility
- **Number of components:** the application can be extended easily to allow for more than 2 components and for more than 1 type of finished product
  - For example, components `ABCDE` may produce product `F` (with `ABC`) or product `G` (with `DE`)
- **Duration of assembly:** it is relatively easy to customise the duration of assembly per type of finite product or by other criteria
- **Worker behaviour:** given that workers are state machines, altering their behaviour is relatively easy by providing for more states and more state transitions
