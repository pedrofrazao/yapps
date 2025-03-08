# agent.direction_selector
from random import randint

def random_direction_selector( context, curr_dir=None, prob_change=30 ):
    if curr_dir is None:
        return randint(1,9)
    elif randint(1,100) > prob:
        return curr_dir
    else:
        return randint(1,9)

