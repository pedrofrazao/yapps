import importlib

from ppSlib.arena_sync_model import ArenaSyncModel, asmObject, asmState
from ppSlib.agent_direction_selector import random_direction_selector
from abc import abstractmethod, ABC
from random import randint
import json

# ##
# ## Agent State
# ##
# class AgentState(asmState):
#     def __init__(self, energy=100, direction=5, epoch_penalty=1, **kwargs ):
#         # self.owner = owner
#         _state = kwargs
#         if _state.get('energy', None) is None:
#            _state['energy'] = 100
#         if _state.get('epoch_penalty', None) is None:
#             _state['epoch_penalty'] = 1
#         if _state.get('direction',None) is None:
#             _state['direction'] = 5
#         super().__init__( _state )

#     def epoch_tic(self):
#         self.add2sattr('energy', self.getsattr('epoch_penalty') )

#     # def change_energy_by(self, delta):
#     #     self.energy += delta

#     # def copy(self):
#     #     return self.clone()

#     def __str__(self):
#         return f"{self.energy}"
    
#     def getsattr(self, attr):
#         s = self.get_curr_state()
#         return s.get(attr, None)
    
#     def setsattr(self, attr, value):
#         ns = self.get_next_state()
#         ns[attr] = value

#     def add2sattr(self, attr, value):
#         ns = self.get_next_state()
#         ns[attr] = ns[attr] + value
    
#     @staticmethod
#     def Agent.add_to_state_args( s_args, **kwargs ):
#         ## add s_args dict values to a state_args present on kwargs
#         state = kwargs.get('state_args', {})
#         for k,v in s_args.items():
#             state[k] = v if k not in state else state[k]
#         return state

#     def __str__(self):
#         return f"Energy: {self.energy}, Direction: {self.direction}, Epoch Penalty: {self.epoch_penalty}, State: {str(self._state)}"
    
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
            state = kwargs['state_args']
            del kwargs['state_args']
 
        # self.state = AgentState(state)

        super().__init__( name, state, **kwargs )

    # def run_interaction(self):
    #     ## select action
    #     pass
    #     ## do action
    #     pass

    # def run_update(self):
    #     pass

    @staticmethod
    def add_to_state_args( s_args, **kwargs ):
        ## add s_args dict values to a state_args present on kwargs
        state = kwargs.get('state_args', {})
        for k,v in s_args.items():
            state[k] = v if k not in state else state[k]
        return state

    def get_state(self):
        return self.asmstate

    def epoch_tic(self):
        self.add2sattr('energy', - self.getsattr('epoch_penalty') )

    def run_interaction(self, context=None):
        super().run_interaction(context)
        surroundings = self.see(self.asmstate)
        action,args_action = self.select_action(self.asmstate,surroundings)
        self.do_action(action,args_action)

    def run_update(self, context=None):
        self.epoch_tic()
        super().run_update()
        if(self.energy() < 1):
            self.die()

    def die(self):
        if(self.log):
            self.log( "died" )
        self.arena.remove_from_position(self.x, self.y, self)

    def select_action(self,state,surroundings):
        # return action, action_args
        return None, None

    def energy(self):
        return self.getsattr('energy')
    
    def direction(self):
        return self.getsattr('direction')
    
    def see(self,state=None):
        pass

    def do_action(self,action,action_args):
        pass

    def action_recipient(self,action,from_agent=None):
        pass

    def move(self, direction, distance=1):
        return self.arena.move_object_position(self, direction, distance)
   
    # def getsattr(self, attr):
    #     return self.state.getsattr(attr)
    
    # def setsattr(self, attr, value):
    #     self.state.setsattr(attr, value)

    # def add2sattr(self, attr, value):
    #     self.state.add2sattr(attr, value)

    # def get_next_obj_state(self):
    #     return self.state.get_next_state()

    def __str__(self):
        return f"{self.nickname}"

    def info(self, class_name=False, multi_line=False):
        if( class_name is False and multi_line is False ):
            return f"e{self.energy()} d{self.getsattr("direction")} - {self.msg[-1:]}"
        else:
            msg = f"{self.nickname}"
            if( class_name ):
                msg += f" {self.__class__.__name__}"
            msg += f" - e{self.energy()} d{self.getsattr("direction")}"
            if( multi_line ):
                msg += "\n" + "\n".join(self.msg[-3:])
            else:
                msg += f"\n{self.msg[-1:]}"
            return msg
    

#
# base class for nonliving agents
# - no move
# - no dying
#
class NonlivingAgent(Agent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = { 'epoch_penalty': 0 }
        kwargs['can_move'] = kwargs.get('can_move', False)
        super().__init__( **kwargs )

    def run_interaction(self, context=None):
        pass

    def run_update(self, context=None):
        pass

    # this agent can't die
    def die(self):
        pass

#
# base class for living agents
# - can move
# - can die
# - has energy
#
class LivingAgent(Agent):
    ## accept a direction selector function
    ## - LivingAgent( select_direction=lambda surrounding: randint(1,9) if randint(1,10) > 7 else self.direction() )
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        kwargs['state_args'] = Agent.add_to_state_args( { 'move_distance': 1 }, **kwargs )
        # if 'select_direction' in kwargs:
        #     if callable(kwargs['select_direction']):
        #         self.direction_selector = kwargs['select_direction']
        #     elif isinstance(kwargs['select_direction'], tuple):
        #         self.select_direction_func_name = kwargs['select_direction'][0]
        #         self.select_direction_func_kwargs = kwargs['select_direction'][1]
        #         self.direction_selector = globals().get(self.select_direction_func_name)
        #     else:
        #         raise ValueError("select_direction must be callable")
        #     del kwargs['select_direction']
        # else:
        #     self.select_direction_func_kwargs = { 'curr_dir': None, 'prob_change': 30 }
        #     self.direction_selector = random_direction_selector

        super().__init__( **kwargs )

    # def select_direction(self, surrounding=None):
    #     return self.direction_selector(surrounding, **self.select_direction_func_kwargs)

    def do_action(self,action,action_args):
        if( action == "move" ):
            return self.move(action_args['direction'], self.getsattr('move_distance') )
        else:
            raise ValueError("Unknown action")
        
    def _random_direction_selector(self, prob_change=30):
        if( randint(1,100) < prob_change ):
            dir = randint(1,9)
            self.setsattr('direction',dir)
        else:
            return self.getsattr('direction')
        
    def action_recipient(self, action, from_agent=None):
        if('eat' == action):
            self.die()
            self.add_msg( f"{from_agent.name} eaten" )

class Block(NonlivingAgent):
    def __init__(self, **kwargs):
        super().__init__( can_move=False, volume=100,priority=10, **kwargs )


class Trap(NonlivingAgent):
    def __init__(self, **kwargs):
        super().__init__( can_move=False, volume=1, priority=10, **kwargs )

    def see(self, _):
        # get agents at the same position as the trap
        c = self.arena.get_pos_surrounding(self.x, self.y, length=0)
    
        for obj,dr,ds in c:
            if( obj.id != self.id ):
                obj.die()
                self.add_msg( f"trap: {obj.name}" )
                obj.add_msg( f"{obj.name} trapped")


class Prey(LivingAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args( { 'energy':20, 'epoch_penalty': 0 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)
        super().__init__( volume=33, **kwargs )

    # def run_interaction(self):
    #     super().run_interaction()
    #     # c = self.arena.get_pos_surrounding(self.x, self.y)
    #     ## change direction?
    #     self.setsattr( 'direction', self.select_direction() )

    #     self.arena.move_object_position(self, self.getsattr('direction'), 1)
    def see(self,_):
        return None
    
    def select_action(self, state, surroundings):
        dir = randint(1,9)
        self.setsattr('direction', dir)
        return "move", { 'direction': dir }

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
        kwargs['state_args'] = Agent.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)
        super().__init__( volume=33, **kwargs )
    
    def select_action(self, state, surroundings):
        return 'move', { 'direction': self.dir }

class Predator(LivingAgent):
    def __init__(self, see_length=2, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 5)
        self.see_length = see_length
        super().__init__( volume=33, **kwargs )

    def see(self, state):
        return self.arena.get_pos_surrounding(self.x, self.y, length=self.see_length).sorted()
        
    def select_action(self, state, surroundings):
        energy = state.getsattr('energy')
        if energy > 20:
            ## i'm ok, do nothing
            return None, None
        else:
            ## i'm hungry
            action, action_args = None, {}
        
            for o,dis,dir in sorted(surroundings):
                if( not isinstance(o, LivingAgent) or isinstance(o, self.__class__) ):
                    ## only eat LivingAgent but I'm not a cannibal
                    continue
                else:
                    action_args['agent']=o
                    action_args['distance']=dis
                    action_args['direction']=dir
                    break
        
        if( action_args.get('agent', None) is None ):
            ## no target, just move
            dir = self._random_direction_selector()
            return 'move', { 'direction': dir }
        
        ## prey found!!
        self.setsattr('direction', action_args['direction'])

        if( action_args['distance'] <= 1 ):
            ## eat
            return 'eat', action_args
        else:
            ## move to the prey
            return 'move', action_args

    def do_action(self, action, action_args):
        if( action == 'eat' ):
            self.eat(action_args)
        elif( action == 'move' ):
            self.move(action_args['direction'], action_args.get('distance', 1))

    def eat(self, action_args):
        if(action_args['distance'] > 0):
            self.move(action_args['direction'], action_args['distance'])

        target = action_args['agent']
        if( self.arena.distance_between_objects(self, target) > 1 ):
            self.add_msg( f"too far - move to: {target.name}" )
        else:
            target.action_recipient('eat',from_agent=self)
            self.add_msg( f"eat: {target.name}" )
            self.add2sattr('energy', 10)
        

class Carnivore(Predator):
    pass
    # def __init__(self, **kwargs):
    #     super().__init__( **kwargs )

# class Trap(NonlivingAgent):
#     def __init__(self, **kwargs):
#         super().__init__( can_move=False, volume=1, priority=10, **kwargs )

#     def run_interaction(self, context=None):
#         c = self.arena.get_pos_surrounding(self.x, self.y, length=0)
    
#         for obj,dr,ds in c:
#             if( obj.id != self.id ):
#                 obj.die()
#                 obj.add_msg( f"{obj.name} trapped")


class Grass(NonlivingAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args( { 'epoch_penalty': 0 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)
        super().__init__( can_move=False, volume=1, **kwargs )

    def run_interaction(self, context=None):
        pass

    def run_update(self, context=None):
        pass

    def die(self):
        super().die()
        obj = Grass( state_args={}, arena=self.arena)
        self.arena.add_to_random_position(obj, empty=True)
        if(self.log):
            self.log( "reborn" )


class PluginBaseAgent():
    @classmethod
    def Load(cls, agent_model_data):

        if( 'class' not in agent_model_data 
            or 'name' not in agent_model_data ):
            return "Error: The config file has a unknown format"
        
        try:
            agent_class = globals().get(agent_model_data['class'])
            if agent_class is None:
                # try to load the class from plugin directory
                from importlib import import_module
                try:
                    amodel = agent_model_data['class'].split('.')[0]
                    aclass = agent_model_data['class'].split('.')[1]
                    loadclass = importlib.import_module('models.'+amodel)
                    agent_class = getattr(loadclass,aclass)
                except Exception as e:
                    return f"Error: The class {agent_model_data['class']} is not defined."
            
            state = {}
            if 'state' in agent_model_data:
                agent = agent_class(name=agent_model_data['name'], state_args=agent_model_data['state'] )
            else:
                agent = agent_class(name=agent_model_data['name'] )
        except Exception as e:          
            return f"Error: {e}"
        
        return agent

    # @abstractmethod
    # def run_interaction(self):
    #     pass

    # @abstractmethod
    # def run_update(self):
    #     pass
