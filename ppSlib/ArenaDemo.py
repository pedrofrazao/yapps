from ppSlib.arena_sync_model import ArenaSyncModel
from ppSlib.agent import Agent, AgentState, Carnivore, Prey, Block, Trap, LivingAgent
from random import randint

def load_demo( case = 1, **kwargs ):

    return _load_demo_1( **kwargs )


def _load_demo_1( **kwargs ):
    rows = kwargs.get('rows', 16)
    cols = kwargs.get('cols', 16)

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