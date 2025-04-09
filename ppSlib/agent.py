import importlib

from ppSlib.arena_sync_model import ArenaSyncModel, asmObject, asmState
from ppSlib.agent_direction_selector import random_direction_selector
from ppSlib.asmStats import asmObjectStat
from ppSlib.action import action, move, action_selection, mate, rest
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
            raise ValueError("state not allowed in kwargs")
        elif 'state_args' in kwargs:
            state = kwargs['state_args'].copy()
            del kwargs['state_args']
 
        if 'actions' in kwargs:
            actions = kwargs['actions']
            del kwargs['actions']
        else:
            actions = []
        self._action_selector = action_selection( actions=actions )
        
        # extract some asmObject attributes
        for k in ('volume', 'priority'):
            if k in state:
                kwargs[k] = state[k]
                del state[k]

        state['age'] = 0
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

    def species(self):
        return self.__class__.__name__

    def run_interaction(self, context=None):
        super().run_interaction(context)
        # see
        surroundings = self.see(self.asmstate)
        self.asmstate.t_set_attr('surroundings', surroundings)
        # select action
        oaction,args_action = self.select_action(self.asmstate)

        if oaction is not None:
            self.add_msg( f"{oaction.name} - {args_action}" )
            self.asmstate.t_set_attr('ran action', oaction)
            oaction.run_action(self,self.get_state(),args_action)

    def age(self):
        return self.getsattr('age')

    def run_update(self, context=None):
        state = self.get_state()
        ran_action = state.t_get_attr('ran action', None)
        if ran_action is not None:
            ran_action.action_update_phase(self,state)
        
        self.add2sattr('energy', - self.getsattr('epoch_penalty') )
        self.add2sattr('age', 1)

        super().run_update()
        if(self.energy() <= 0):
            self.die()


    def eaten(self):
        self.add_msg( f"{self.nickname} eaten" )
        self.die()

    def die(self):
        if(self.log):
            self.log( "died" )
        self.arena.remove_from_position(self.x, self.y, self)


    def select_action(self,state):
        """
        return: action, action_args
        """
        utilities = self._action_selector.calculate_utility(state=state)
        ta =  utilities.get_top_action_list()
        (action, u, action_args) = ta[0] if len(ta) > 0 else (None, None, None)
        return action, action_args
    

    def energy(self):
        return self.getsattr('energy')
    
    def direction(self):
        return self.getsattr('direction')
    
    def see(self,state=None):
        x,y = self.x, self.y
        dir = self.direction()
        see_length = self.getsattr('see_length',1)
        saw = self.arena.get_pos_surrounding(x, y, dir, see_length, exclude_obj=self)
        return saw

    def do_action(self,action,action_args):
        pass

    # def action_recipient(self,action,from_agent=None):
    #     pass

    def move(self, direction, distance=1):
        return self.arena.move_object_position(self, direction, distance)

    @classmethod
    def _filter_surroundings(cls, surroundings, obj_class):
        return [ (o,dr,ds) for o,dr,ds in surroundings if isinstance(o, obj_class) ]

    def __str__(self):
        return f"{self.nickname}"

    def _more_internal_state_info(self):
        return ""
    
    def _info_lstmsg(self):
        return self.get_last_msg()

    def info(self, class_name=False, multi_line=False, onlywithmessage=False):
        if( onlywithmessage and len(self.msg) == 0 ):
            return None
        if( class_name is False and multi_line is False ):
            return f"e{self.energy()} a{self.getsattr('age')} d{self.getsattr("direction",0)} {self._more_internal_state_info()}- {self._info_lstmsg()}"
        else:
            msg = f"{self.nickname}"
            if( class_name ):
                msg += f" {self.__class__.__name__}"
            msg += f" - e{self.energy()} d{self.getsattr("direction")}"
            if( multi_line ):
                msg += self._more_internal_state_info()
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
        # store the initial state args for the mate function
        self._init_state_args = kwargs['state_args'].copy()

        kwargs['state_args'] = Agent.add_to_state_args( { 'see_length': 0 }, **kwargs )
        kwargs['state_args'] = Agent.add_to_state_args( { 'epoch_penalty': 1 }, **kwargs )
        kwargs['state_args'] = Agent.add_to_state_args( { 'move_distance': 1 }, **kwargs )
        kwargs['state_args'] = Agent.add_to_state_args({'age': 0}, **kwargs)
        if dir == 5:
            dir = random_direction_selector()

        kwargs['state_args'] = Agent.add_to_state_args( { 'direction': dir, 'epoch_penalty': 0 }, **kwargs )

        super().__init__( **kwargs )
        asmObjectStat.__init__(self, **kwargs)
        
    def mated(self):
        self.asmstate.t_set_attr('mated', True)

    def mate(self, partner, mate_params, **kwargs):
        partner.mated()
        new_state_args = self._init_state_args.copy()
        return [ self.__class__( state_args = new_state_args, arena=self.arena,
                                 actions = self._action_selector.actions_list, **kwargs ) ]

    def stats(self):
        return [self.energy(),self.getsattr('age'),self.direction(), self.get_last_msg()]
    


class LivingGAAgent(LivingAgent):
    def __init__(self, **kwargs):
        if( not hasattr(self, 'chromosome') and 'chromosome' not in kwargs ):
            raise ValueError("chromosome not defined for a ".self.__class__.__name__)

        self.chromosome = kwargs['chromosome'] if isinstance( kwargs['chromosome'], Chromosome ) else Chromosome( kwargs['chromosome'])
        del kwargs['chromosome']

        super().__init__( **kwargs )
        
        ## apply the chromosome to the state
        self.chromosome.phenotype(self.get_state())

    def get_gene(self,name):
        return self.chromosome.gene_value(name)
    
    def mate(self, partner, mate_params):
        new_state_args = self._init_state_args.copy()
        chrom = self.chromosome.crossover(partner.chromosome)
        return [ self.__class__( state_args = new_state_args, arena=self.arena, chromosome=chrom ) ]
        
    def _more_internal_state_info(self):
        return f"c:{self.chromosome}"


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
        kwargs['priority'] = kwargs.get('priority', 25)
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
        kwargs['state_args'] = Agent.add_to_state_args( { 'energy':10, 'direction': dir, 'epoch_penalty': 0, 'change_direction_prob': 0.1 }, **kwargs )
        kwargs['priority'] = kwargs.get('priority', 5)
        change_direction_prob = kwargs['state_args']['change_direction_prob']

        if 'actions' not in kwargs:
            kwargs['actions'] = [ move({ 'distance': 1, 'energy_penalty': 0, 'change_direction_prob': change_direction_prob}) ]
        super().__init__( volume=33, **kwargs )


class GlideGA(LivingGAAgent):
    pass

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

    # def select_action(self, state, surroundings):
    #     if( state.getsattr('energy') >= state.getsattr('max_energy') ):
    #         return None, None
        
    #     grass = Agent._filter_surroundings(surroundings.sorted(), Grass)
    #     if( len(grass) > 0 and grass[0][1] == 0 ):
    #         return 'eat', { 'grass': grass[0][0] }
    #     elif( len(grass) > 0 ):
    #         self.setsattr('direction', grass[0][2])
    #         return 'move', { 'direction': grass[0][2] }
    #     else:
    #         self._random_direction_selector()
    #         return 'move', {}

    # def do_action(self, action, action_args):
    #     if action == 'eat':
    #         target = action_args['grass']
    #         target.action_recipient('eat', from_agent=self)
    #         self.add2sattr('energy', 3)
    #         self.log( f"eat: {target.nickname}" )
    #     else:
    #         super().do_action(action, action_args)

    # def die(self):
    #     super().die()

class Grass(LivingAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args({ 'volume':1, 'energy':1,
                                                         'epoch_penalty': 0,'see_length':1,
                                                         'min_matetime': 5,
                                                         },
                                                         **kwargs )
        kwargs['priority'] = kwargs.get('priority', 5)

        actions = [ mate( { 'mate_species': [Grass],
                            'utility_value': 10,
                            'minimal_energy': 10,
                            'nearby_distance': 1, 
                            'penalty_species': [],
                            'penalty_count_factor': 0,
                            'penalty_distance_factor':0,
                            'energy_penalty': 9 } ),
                    rest( { 'energy_recover': 2, 'max_recoverable_energy': 20 } ),
        ]

        kwargs['actions'] = actions

        super().__init__( can_move=False, **kwargs )


class Grass2(LivingGAAgent):
    def __init__(self, **kwargs):
        kwargs['state_args'] = Agent.add_to_state_args({ 'volume':1, 'energy':1,
                                                         'epoch_penalty': 0,'see_length':1,
                                                         'min_matetime': 5,
                                                         },
                                                         **kwargs )
        kwargs['priority'] = kwargs.get('priority', 5)
        kwargs['chromosome'] = kwargs.get('chromosome',
                                          [ ('rest|energy_recover',[1,5,10,20],"" ),
                                            # ('mate|energy_penalty',[0,1,2,3,4,5],"" ),
                                            # ('mate|near_by_distance',[0,1,2],""),
                                            ('see_length',[2,3],"" ),
                                          ])

        actions = [ mate( { 'mate_species': [Grass2],
                            'utility_value': 10,
                            'minimal_energy': 10,
                            'nearby_distance': 1,
                            'penalty_species': [],
                            'penalty_count_factor': 0,
                            'penalty_distance_factor': 0,
                            'energy_penalty': 9, } ),
                    rest( { 'energy_recover': 2, 'max_recoverable_energy': 20 } ),
        ]

        kwargs['actions'] = actions

        super().__init__( can_move=False, **kwargs )


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