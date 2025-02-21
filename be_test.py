#!/usr/bin/env python3
import sys
import os
from random import randint
import curses

dirname = os.path.dirname(__file__)
sys.path.append(dirname)

from ppSlib.arena_sync_model import ArenaSyncModel
from ppSlib.agent import Agent, AgentState

rows=10
cols=10

class block(Agent):
    def __init__(self, arena=None):
        super().__init__( "B", state={}, arena=arena)

    def __str__(self):
        return "XX"

class prey(Agent):
    def __init__(self,state={}, priority=10, arena=None):
        super().__init__( f"p{prey.id}", AgentState(self,**state), priority=priority, arena=arena )
        prey.id += 1

    def run_interaction(self, context=None):
        s = self.get_obj_state()
        c = self.arena.get_pos_surrounding(self.x, self.y)
    
        if( randint(1,10) > 7 ):
            s.direction = randint(1,9)
    
        if(s.energy > 5 and self.arena is not None ):
            self.arena.move_object_position(self, s.direction, 1)
        else:
            self.add_msg( f"low energy stop moving" )

    def run_update(self, context=None):
        s = self.get_obj_state()
        s.energy -= 1
        self.set_obj_state(s)
        if(s.energy < 1):
            self.die()
        # if(self.log):
        #     self.log( f"update: {self.name}" )

    def die(self):
        if(self.log):
            self.log( f"die: {self.name}" )
        self.arena.remove_from_position(self.x, self.y, self)

    def __str__(self):
        return f"{self.name}"
    
    # def _info(self):
    #     msg = self.msg
    #     msg.insert(0, f"{self.name}" )
    #     msg.insert(1, f"energy: {self.get_obj_state()['energy']}" )
    #     return "\n".join(msg)

def main(stdscr):
    # Initialize the arena and objects
    arena = ArenaSyncModel(rows, cols, sync_model='Sync')
    obj1 = prey( { 'energy':10, 'direction':9}, arena=arena)
    obj2 = prey( { 'energy':20, 'direction':9}, arena=arena)
    arena.add_to_position(0, 0, obj1)
    arena.add_to_position(0, 1, obj2)

    blocks = [ block({}) for i in range(int(cols*3/4)) ]
    br = int(rows/2)
    bc = randint(1,cols-1)
    for b in blocks:
        arena.add_to_position(br, bc, b)
        bc += 1
        bc = bc % cols
    

    # Run the loop with curses
    loop(stdscr, arena, 20)

    height, width = stdscr.getmaxyx()
    stdscr.addstr(height - 1, 0, "Press 'q' to exit.")
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break

def loop(stdscr, arena, steps=5):
    for i in range(steps):
        # Clear the screen
        stdscr.clear()

        # Display the arena
        stdscr.addstr(0, 0, str(arena))
        stdscr.addstr(rows+2, 0, "====")
        stdscr.addstr(rows+4, 0, arena.objects_info())

        # Refresh the screen to show the updated arena
        stdscr.refresh()

        # Run a step in the arena
        arena.run_step()

        # Wait for a short period to create a visual effect
        curses.napms(5000)

if __name__ == "__main__":
    curses.wrapper(main)


