# agent.direction_selector
from random import randint, choice, random

def random_direction_selector( curr_dir=None, prob_change=1 ):
    if curr_dir is None:
        return choice([1,2,3,4,6,7,8,9])
    elif random() > prob_change:
        return curr_dir
    else:
        nd = choice([1,2,3,4,6,7,8,9])
        if nd == curr_dir:
            l = [1,2,3,4,6,7,8,9]
            l.remove(curr_dir)
            nd = choice(l)
            
        return nd
