#!/usr/bin/env python3
import sys
import os
from random import randint
import curses

dirname = os.path.dirname(__file__)
sys.path.append(dirname)

from ppSlib.arena_sync_model import ArenaSyncModel
from ppSlib.agent import Agent, AgentState, Carnivore, Prey, Block, Trap, LivingAgent

rows=16
cols=16

def main(stdscr):
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

    # Display the arena
    stdscr.addstr(0, 0, str(arena))
    stdscr.addstr(rows+2, 0, "====")

    # Run the loop with curses
    loop(stdscr, arena, 4000)

    height, width = stdscr.getmaxyx()
    stdscr.addstr(height - 1, 0, "Press 'q' to exit.")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break


def loop(stdscr, arena, steps=5):
    num_rows, num_cols = stdscr.getmaxyx()
    lwin = curses.newpad(num_rows*10, 255 )
    c = None

    for i in range(steps):
        # Run a step in the arena
        msg = []
        arena.run_step()
        for obj in sorted(arena.get_objects(), key=lambda x: x.nickname):
            if( isinstance(obj, LivingAgent) ): 
                # msg.extend( [ f"{obj.nickname}-{m}" for m in obj.msg[-2:]] )
                msg.extend( [ f"{obj.nickname}-{obj.info()}" ] )

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
        if( c is not None and c == ord('q') ):
            break
        elif( c is not None and c == ord('c') ):
            stdscr.timeout(100)  # Set timeout for getch to 100 milliseconds
            c = stdscr.getch()
        else:
            stdscr.timeout(80000000)
            c = stdscr.getch()
        

if __name__ == "__main__":
    curses.wrapper(main)

