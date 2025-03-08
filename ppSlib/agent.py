from ppSlib.arena_sync_model import ArenaSyncModel, asmObject
from ppSlib.agent_direction_selector import random_direction_selector
from abc import abstractmethod, ABC
from random import randint

##
## Agent State
##
class AgentState:
    def __init__(self, owner, age=0, energy=100, direction=5, female=True, move_dir=None, move_len=None, epoch_penalty=1):
        self.owner = owner
        self.energy = energy
        self.age = age
        self.direction = direction
        self.female = female
        self.move_dir = move_dir
        self.move_len = move_dir
        self.epoch_penalty = epoch_penalty

    def clone(self):
        return AgentState(
            owner = self.owner,
            age=self.age,
            energy=self.energy,
            direction=self.direction,
            female=self.female,
            move_dir=self.move_dir,
            move_len=self.move_len,
            epoch_penalty = self.epoch_penalty
        )

    def epoch_tic(self):
        self.energy -= self.epoch_penalty
        self.age += 1

    def change_energy_by(self, delta):
        self.energy += delta

    def copy(self):
        return self.clone()

    def __str__(self):
        return f"{self.energy}"
    
    @staticmethod
    def add_to_state_args( s_args, **kwargs ):
        ## add s_args dict values to a state_args present on kwargs
        state = kwargs.get('state_args', {})
        for k,v in s_args.items():
            state[k] = v if k not in state else state[k]
        return state
    
##
## Agent
##
class Agent(asmObject):

    def __init__(self, name=None, **kwargs):
        state = None 
        if 'state' in kwargs:
            state = kwargs['state']
            del kwargs['state']
        elif 'state_args' in kwargs:
            state = AgentState(self, **kwargs['state_args'])
            del kwargs['state_args']
        else:
            state = AgentState(self)
        super().__init__( name, state, **kwargs )

    # def run_interaction(self):
    #     ## select action
    #     pass
    #     ## do action
    #     pass

    # def run_update(self):
    #     pass

    def run_update(self, context=None):
        s = self.get_next_obj_state()
        if not isinstance(s, AgentState):
            return
        
        s.epoch_tic()
        self.set_obj_state(s)
        if(s.energy < 1):
            self.die()
        ## commit the changes on the state
        super().run_update()

    def die(self):
        if(self.log):
            self.log( "died" )
        self.arena.remove_from_position(self.x, self.y, self)

    def _select_action(self):
        return self.logic.select_action()

    def energy(self):
        return self.state.energy
    
    def direction(self):
        return self.state.direction

    def __str__(self):
        return f"{self.nickname}"
    
    def info(self):
        return f"e{self.energy()} d{self.state.direction} - {self.msg[-1:]}"

class NonlivingAgent(Agent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = { 'epoch_penalty': 0 }
        kwargs['can_move'] = kwargs.get('can_move', False)
        super().__init__( **kwargs )
        
    # this agent can't die
    def die(self):
        pass

class LivingAgent(Agent):
    ## accept a direction selector function
    ## - LivingAgent( select_direction=lambda surrounding: randint(1,9) if randint(1,10) > 7 else self.direction() )
    def __init__(self, **kwargs):
        kwargs['state_args'] = AgentState.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        if 'select_direction' in kwargs:
            if callable(kwargs['select_direction']):
                self.direction_selector = kwargs['select_direction']
            elif isinstance(kwargs['select_direction'], tuple):
                self.select_direction_func_name = kwargs['select_direction'][0]
                self.select_direction_func_kwargs = kwargs['select_direction'][1]
                self.direction_selector = globals().get(self.select_direction_func_name)
            else:
                raise ValueError("select_direction must be callable")
            del kwargs['select_direction']
        else:
            self.select_direction_func_kwargs = { 'curr_dir': None, 'prob_change': 30 }
            self.direction_selector = random_direction_selector

        super().__init__( **kwargs )

    def select_direction(self, surrounding=None):
        return self.direction_selector(surrounding, **self.select_direction_func_kwargs)

class Block(NonlivingAgent):
    def __init__(self, **kwargs):
        super().__init__( can_move=False, volume=100,priority=10, **kwargs )

    def run_interaction(self, context=None):
        pass

    def run_update(self, context=None):
        pass

class Trap(NonlivingAgent):
    def __init__(self, **kwargs):
        super().__init__( can_move=False, volume=1, priority=10, **kwargs )

    def run_interaction(self, context=None):
        s = self.get_obj_state()
        c = self.arena.get_pos_surrounding(self.x, self.y, length=0)
    
        for obj,dr,ds in c:
            if( obj.id != self.id ):
                obj.die()
                self.add_msg( f"trap: {obj.name}" )
                obj.add_msg( f"{obj.name} trapped")

    def run_update(self, context=None):
        pass


class Prey(LivingAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = AgentState.add_to_state_args( { 'epoch_penalty': 0 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)
        super().__init__( volume=33, **kwargs )

    def run_interaction(self):
        super().run_interaction()
        s = self.get_next_obj_state()

        # c = self.arena.get_pos_surrounding(self.x, self.y)
        ## change direction?
        s.direction = self.select_direction()

        self.arena.move_object_position(self, s.direction, 1)
        self.set_obj_state(s)

    # override the die method to generate a new prey on a random position
    def die(self):
        super().die()
        energy = randint(20,40)
        obj = Prey( state_args={ 'energy':energy}, arena=self.arena)
        self.arena.add_to_random_position(obj)
        if(self.log):
            self.log( "reborn" )
    
class Glide(LivingAgent):
    def __init__(self, dir=8, **kwargs):
        self.dir = dir
        kwargs['state_args'] = AgentState.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)
        super().__init__( volume=33, **kwargs )
    
    def run_interaction(self):
        super().run_interaction()
        self.arena.move_object_position(self, self.dir, 1)

class Predator(LivingAgent):
    def __init__(self, see_length=2, **kwargs):
        kwargs['state_args'] = AgentState.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 5)
        self.see_length = see_length
        super().__init__( volume=33, **kwargs )

    def run_interaction(self):
        super().run_interaction()
        
        s = self.get_next_obj_state()
        if s.energy > 20:
            ## i'm ok, do nothing
            return
        
        srrn = self.arena.get_pos_surrounding(self.x, self.y, length=self.see_length).sorted()

        target=(None,None,None)
        for o,dis,dir in sorted(srrn):
            if( not isinstance(o, LivingAgent) or isinstance(o, self.__class__) ):
                ## only eat LivingAgent but I'm not a cannibal
                continue
            else:
                target = (o,dis,dir)
                break
        
        if( target[0] is None ):
            ## no target, just more
            s.direction = self.select_direction()
        else:
            s.direction = target[2]

        if( target[0] is not None and target[1] <= 1 ):
            ## eat
            o = target[0]
            o.die()
            self.add_msg( f"eat: {o.nickname}" )
            s.energy += 10
        else:
            self.add_msg( f"move: {s.direction}" )
        ## move
        self.arena.move_object_position(self, s.direction, 1)
        self.set_obj_state(s)

class Carnivore(Predator):
    pass
    # def __init__(self, **kwargs):
    #     super().__init__( **kwargs )

class Trap(NonlivingAgent):
    def __init__(self, **kwargs):
        super().__init__( can_move=False, volume=1, priority=10, **kwargs )

    def run_interaction(self, context=None):
        s = self.get_obj_state()
        c = self.arena.get_pos_surrounding(self.x, self.y, length=0)
    
        for obj,dr,ds in c:
            if( obj.id != self.id ):
                obj.die()
                obj.add_msg( f"{obj.name} trapped")

