import importlib

from ppSlib.arena_sync_model import ArenaSyncModel, asmObject, asmState
from ppSlib.agent_direction_selector import random_direction_selector
from ppSlib.asmStats import asmObjectStat
from ppSlib.action import action, move, action_selection
from ppSlib.genetic import Chromosome
from abc import abstractmethod, ABC
from random import randint, choice

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
    """
    run_interaction() - run the interaction with the arena
      - see() - get the surroundings
      - select_action() - select the action to do
      - do_action() - do the action

    run_update() - run the update of the agent
      - change the state of the agent
      - if energy < 1, die()
    """
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


    @staticmethod
    def add_to_state_args( s_args, **kwargs ):
        ## add s_args dict values to a state_args present on kwargs
        state = kwargs.get('state_args', {})
        for k,v in s_args.items():
            state[k] = v if k not in state else state[k]
        return state

    def get_state(self):
        return self.asmstate


    def run_interaction(self, context=None):
        super().run_interaction(context)
        surroundings = self.see(self.asmstate)
        action,args_action = self.select_action(self.asmstate,surroundings)
        self.do_action(action,args_action)

    def run_update(self, context=None):
        self._move_update()
        self.add2sattr('energy', - self.getsattr('epoch_penalty') )
        self.add2sattr('age', 1)
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
        x,y = self.x, self.y
        see_length = self.getsattr('see_length',1)
        return self.arena.get_pos_surrounding(x, y, see_length)

    def do_action(self,action,action_args):
        pass

    # def action_recipient(self,action,from_agent=None):
    #     pass

    def move(self, direction, distance=1):
        if( direction is not None ):
            self.asmstate.t_set_attr('_arena_move', (direction,distance) )
    
    def _move_update(self):
        params = self.asmstate.t_get_attr('_arena_move', None)
        if params is not None:
            direction,distance = params
            return self.arena.move_object_position(self, direction, distance)

    @classmethod
    def _filter_surroundings(cls, surroundings, obj_class):
        return [ (o,dr,ds) for o,dr,ds in surroundings if isinstance(o, obj_class) ]

    def __str__(self):
        return f"{self.nickname}"

    def info(self, class_name=False, multi_line=False, onlywithmessage=False):
        if( onlywithmessage and len(self.msg) == 0 ):
            return None
        if( class_name is False and multi_line is False ):
            return f"e{self.energy()} a{self.getsattr('age')} d{self.getsattr("direction",0)} - {self.msg[-1:]}"
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
    """
    no run_interaction
    no run_update
    no die
    """
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
class LivingAgent(Agent,asmObjectStat):
    """
    added state_args:
    - age
    - epoch_penalty
    - move_distance
    """
    ## accept a direction selector function
    ## - LivingAgent( select_direction=lambda surrounding: randint(1,9) if randint(1,10) > 7 else self.direction() )
    def __init__(self, dir=5, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args( { 'see_length': 0 }, **kwargs )
        kwargs['state_args'] = Agent.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        kwargs['state_args'] = Agent.add_to_state_args( { 'move_distance': 1 }, **kwargs )
        kwargs['state_args'] = Agent.add_to_state_args({'age': 0}, **kwargs)
        kwargs['state_args'] = Agent.add_to_state_args( { 'direction': dir, 'epoch_penalty': 0 }, **kwargs )

        if 'actions' in kwargs:
            actions = kwargs['actions']
            del kwargs['actions']
        else:
            actions = []
        self._action_selector = action_selection( actions=actions )

        if 'chromosome' in kwargs:
            self.chromosome = Chromosome( kwargs['chromosome'] )
            del kwargs['chromosome']

        super().__init__( **kwargs )
        asmObjectStat.__init__(self, **kwargs)

        ## apply the chromosome to the state
        if( hasattr(self, 'chromosome') ):
            self.chromosome.apply_to_state(self.get_state())
        
        
    # def select_direction(self, surrounding=None):
    #     return self.direction_selector(surrounding, **self.select_direction_func_kwargs)

    def run_update(self, context=None):
        super().run_update(context)

    def stats(self):
        return [self.energy(),self.getsattr('age'),self.direction()]
    

    def do_action(self,oaction,action_args):
        if( isinstance( oaction, move ) ):
            params = oaction.run_action(self.get_state())
            self.move( *params )
        elif( isinstance( oaction, action ) ):
            oaction.run_action(self.get_state())
        else:
            raise ValueError("Unknown action: " + str(oaction))
        
    def _random_direction_selector(self, prob_change=30):
        if( randint(1,100) < prob_change ):
            dir = randint(1,9)
            self.setsattr('direction',dir)
        else:
            return self.getsattr('direction')
        
    def action_recipient(self, action, from_agent=None):
        if('eat' == action):
            self.die()
            self.log( f"{from_agent.nickname} eaten" )


    def select_action(self,state,surroundings):
        utilities = self._action_selector.calculate_utility(state=state)
        (a, u) = utilities.get_top_action_list()[0]
        state = self.get_state()
        state.t_set_attr('surroundings', surroundings)
        return a, state


class Block(NonlivingAgent):
    """
    - priority = 10
    example:
    - Block( name="Block", x=0, y=0, arena=arena )
    """
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
                self.log( f"trap: {obj.nickname}" )
                obj.log( f"{obj.nickname} trapped")


class Prey(LivingAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args( { 'energy':20, 'epoch_penalty': 0 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)
        if 'actions' not in kwargs:
            kwargs['actions'] = [ move({ 'distance': 1, 'energy_penalty': 0, 'change_direction_prob': 0}) ]

        super().__init__( volume=33, **kwargs )


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
        kwargs['state_args'] = Agent.add_to_state_args( { 'energy':10, 'direction': dir, 'epoch_penalty': 0 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)

        kwargs['actions'] = [ move({ 'distance': 1, 'energy_penalty': 0, 'change_direction_prob': 0}) ]
        super().__init__( volume=33, **kwargs )



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
            self.log( f"too far - move to: {target.nickname}" )
        else:
            target.action_recipient('eat',from_agent=self)
            self.log( f"eat: {target.nickname}" )
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


class Cow(LivingAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args({ 'energy':20,
                                                         'max_energy': 100,
                                                         'direction': randint(1,9),
                                                         'epoch_penalty': 1 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 5)
        super().__init__( volume=33, **kwargs )

    def select_action(self, state, surroundings):
        if( state.getsattr('energy') >= state.getsattr('max_energy') ):
            return None, None
        
        grass = Agent._filter_surroundings(surroundings.sorted(), Grass)
        if( len(grass) > 0 and grass[0][1] == 0 ):
            return 'eat', { 'grass': grass[0][0] }
        elif( len(grass) > 0 ):
            self.setsattr('direction', grass[0][2])
            return 'move', { 'direction': grass[0][2] }
        else:
            self._random_direction_selector()
            return 'move', {}

    def do_action(self, action, action_args):
        if action == 'eat':
            target = action_args['grass']
            target.action_recipient('eat', from_agent=self)
            self.add2sattr('energy', 3)
            self.log( f"eat: {target.nickname}" )
        else:
            super().do_action(action, action_args)

    def die(self):
        super().die()

class Grass(LivingAgent):
    def __init__(self, **kwargs):
        ## no energy loss
        kwargs['state_args'] = Agent.add_to_state_args({ 'volume':1, 'energy':1,
                                                         'epoch_penalty': 0,'see_length':1,
                                                         'min_matetime': 5,
                                                         },
                                                         **kwargs )
        kwargs['priority'] = kwargs.get('priority', 1)
        super().__init__( can_move=False, **kwargs )

    def select_action(self, state, surroundings):
        if( self.getsattr('age') % self.getsattr('min_matetime') != 0 ):
            return None, None
        pals = Agent._filter_surroundings(surroundings, self.__class__)
        if(len(pals) > 1 and len(pals) <= 4):
            # more than just me and some empty spaces
            return 'mate', { 'pals': pals, 'surr': surroundings }
        else:
            return None, None
        
    def do_action(self, action, action_args):
        if action != 'mate':
            return
        else:
            # mate!
            try:
                x,y = choice( action_args['surr'].empty_pos )
            except:
                x,y = None, None
            if( x is None ):
                if(self.log):
                    self.log( "mated fail, no space" )
            else:
                obj = self.grass_clone()
                if( self.arena.add_to_position(x, y, obj) ):
                    if(self.log):
                        self.log( f"mated at age {self.getsattr('age')}" )
                else:
                    if(self.log):
                        self.log( "mated fail, volume excess" )

    def action_recipient(self, action, from_agent=None):
        if('eat' == action):
            self.die()
            self.log( f"{from_agent.nickname} eaten" )

    def grass_clone(self):
        return Grass( state_args=self.get_obj_state(), arena=self.arena )

    def die(self):
        super().die()
        if(self.log):
            self.log( "died" )

class Wolf(LivingAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args({ 'energy':20,
                                                         'max_energy': 100,
                                                         'direction': randint(1,9),
                                                         'see_length':2,
                                                         'epoch_penalty': 1 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 10)
        super().__init__( volume=55, **kwargs )

    def select_action(self, state, surroundings):
        if( state.getsattr('energy') >= state.getsattr('max_energy') ):
            return None, None
        
        cow = Agent._filter_surroundings(surroundings.sorted(), Cow)
        if( len(cow) > 0 and cow[0][1] <= 1 ):
            self.setsattr('direction', cow[0][2])
            return 'eat', { 'cow': cow[0][0], 'dist': cow[0][1] }
        elif( len(cow) > 1 ):
            self.setsattr('direction', cow[0][2])
            return 'move', { 'direction': cow[0][2] }
        else:
            self._random_direction_selector()
            return 'move', {}

    def do_action(self, action, action_args):
        if action == 'eat':
            target = action_args['cow']
            target.action_recipient('eat', from_agent=self)
            self.add2sattr('energy', 3)
            self.log( f"eat: {target.nickname}" )
            if( action_args['dist'] > 0 ):
                action = 'move'
                action_args = { 'direction': self.getsattr('direction') }
                super().do_action(action, action_args)
        else:
            super().do_action(action, action_args)



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


class GABaseAgent():
    def __init__(self, **kwargs):
        # read GA params
        self.chromo
        self.state['energy'] = kwargs.get('energy', 100)
        self.state['age'] = kwargs.get('age', 0)
        self.state['epoch_penalty'] = kwargs.get('epoch_penalty', 1)
        self.state['direction'] = kwargs.get('direction', 5)