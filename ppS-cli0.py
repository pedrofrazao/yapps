#!/usr/bin/env python3
import sys
import os
from random import randint
import curses
import json

dirname = os.path.dirname(__file__)
sys.path.append(dirname)

from ppSlib.arena_sync_model import ArenaSyncModel
from ppSlib.agent import Agent, Carnivore, Prey, Block, Trap, LivingAgent, Grass
import ppSlib.agent as agent
import datetime
import argparse

rows=16
cols=16



def load_from_file( args ):
    if args.file:
        with open(args.file, 'r') as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error loading configuration: {e}")
                sys.exit(1)
                return
        
        newarena = ArenaSyncModel.deserialize(config)

        return newarena
    else:
        return None


def _load_demo_grass():
    # Initialize the arena and objects
    arena = ArenaSyncModel(16, 16, sync_model='Sync')
    num_grass = 8
    num_cows = 4
    num_wolves = 1

    nearby=[]
    for i in range(num_grass):
        obj = Grass( state_args={ 'age': randint(0,9), 'min_matetime':10, 'energy':1 }, priority=1, arena=arena)
        if( len(nearby) > 0 ):
            x,y = nearby.pop()
            arena.add_to_position(x, y, obj)
        else:
            arena.add_to_random_position(obj)
            nearby = obj.see().find_empty_position()

    for i in range(num_cows):
        obj = agent.Cow(arena=arena, state_args={ 'energy':45}, priority=10)
        arena.add_to_random_position(obj)

    # for i in range(num_wolves):
    #     obj = agent.Wolf(arena=arena, state_args={ 'energy':45}, priority=20)
    #     arena.add_to_random_position(obj)

    return arena

def _load_demo_arena(_):
    return _load_demo_grass()

    # Initialize the arena and objects
    arena = ArenaSyncModel(rows, cols, sync_model='Sync')
    num_traps = 5
    num_prey = 10
    num_predators = 2

    blocks = [ Block(arena=arena) for i in range(int(cols*3/4)) ]
    br = int(rows/2)
    bc = randint(1,cols-1)
    for b in blocks:
        arena.add_to_position(br, bc, b)
        bc += 1
        bc = bc % cols
    
    traps = [ Trap(arena=arena) for i in range(num_traps) ]
    for t in traps:
        arena.add_to_random_position(t)

    for i in range(num_prey):
        energy = randint(20,40)
        obj = Prey( state_args={ 'energy':energy}, arena=arena)
        arena.add_to_random_position(obj)

    for i in range(num_predators):
        energy = randint(20,40)
        obj = Carnivore( state_args={ 'energy':energy}, arena=arena, see_length=3 )
        arena.add_to_random_position(obj)

    return arena

def load_args():
    parser = argparse.ArgumentParser(description='Matrix CLI')
    parser.add_argument('-f', '--file', type=str, help='File to load the arena from')
    parser.add_argument('--epochs', type=int, help='Number of epochs to run', default=100)
    parser.add_argument('--slow', action='store_true', help='Run the simulation slowly', default=False)
    parser.add_argument('--interactive', action='store_true', help='Run the simulation interactively', default=False)
    parser.add_argument('--batch', action='store_true', help='run without output', default=True )
    # parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    if args.interactive is True or args.slow is True:
        args.batch = False

    return args


def main(stdscr, args):

    arena = load_from_file(args)
    if arena is None:
        # load default
        arena = _load_demo_arena(args)

    # arena2 = _load_demo_arena()

    if stdscr is not None:
        # Display the arena
        stdscr.addstr(0, 0, str(arena))
        stdscr.addstr(rows+2, 0, "====")
    else:
        print(arena)

    if stdscr is not None:
        ## init stdscr
        num_rows, num_cols = stdscr.getmaxyx()
        lwin = curses.newpad(num_rows*10, 255 )
        c = None

    def callateachstep(arena, i, msg):
        if stdscr is not None:
            to_cont = stdscr_step(arena, stdscr, lwin, num_rows, num_cols, msg, args)

    # Run the loop with curses
    loop(arena, args.epochs, args, callateachstep)

    if stdscr is None:
        print(arena)
        for i in arena.get_stats():
            if i is not None:
                print(",".join([ str(v) for v in i ]))
        return

    height, width = stdscr.getmaxyx()
    stdscr.addstr(height - 1, 0, "Press 'q' to exit.")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('s'):
            now = datetime.datetime.now()
            filename = f"arena-{now.strftime('%Y%m%d%H%M%S')}.txt"
            with open(filename, 'w') as f:
                json.dump(arena.serialize(), f, indent=4)

            stdscr.addstr(height - 2, 0, f"Arena saved to {filename}")
            stdscr.refresh()


def loop(arena, steps=5, args=None, callateachstep=None):

    for i in range(steps):
        # Run a step in the arena
        msg = []
        arena.run_step()
        for obj in sorted(arena.get_objects(), key=lambda x: x.nickname):
            if( isinstance(obj, LivingAgent) ): 
                # msg.extend( [ f"{obj.nickname}-{m}" for m in obj.msg[-2:]] )
                msg.extend( [ f"{obj.nickname}-{obj.info()}" ] )
            if callateachstep is not None:
                callateachstep(arena, i, msg)


def stdscr_step(arena, stdscr, lwin, num_rows, num_cols, msg, args):
    # Clear the screen
    stdscr.clear()
    lwin.clear()

    # Display the arena
    stdscr.addstr(0, 0, str(arena))
    stdscr.addstr(rows+2, 0, "====")

    for m in msg:
        lwin.addstr(f"{m}\n")
    # Refresh the screen to show the updated arena
    stdscr.refresh()
    # lwin.refresh(0,0, rows+3, 0, num_rows-(rows+2)-1, num_cols-1 )
    lwin.refresh(0,0, rows+3, 0, num_rows-1, num_cols-1 )

    # Wait for a short period to create a visual effect
    if args.interactive is False:
        if args.slow:
            stdscr.timeout(1000)
            c = stdscr.getch()
            if c == -1:
                return True
            elif c == ord('q'):
                return False
        return True

    if( c is not None and c == ord('q') ):
        return False
    elif( c is not None and c == ord('c') ):
        stdscr.timeout(100)  # Set timeout for getch to 100 milliseconds
        c = stdscr.getch()
    else:
        stdscr.timeout(80000000)
        c = stdscr.getch()
        

if __name__ == "__main__":
    args = load_args()
    if args.batch is False:
        curses.wrapper(main, args)
    else:
        main(None, args)


