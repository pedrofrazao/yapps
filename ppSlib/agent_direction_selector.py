# agent.direction_selector
from random import randint, choice

def random_direction_selector( curr_dir=None, prob_change=30 ):
    if curr_dir is None:
        return choice([1,2,3,4,6,7,8,9])
    elif randint(1) > prob:
        return curr_dir
    else:
        return choice([1,2,3,4,6,7,8,9])

