from ppSlib.arena_sync_model import ArenaSyncModel, asmObject
from abc import abstractmethod, ABC
from random import randint


# ##
# ## Agent Logic
# ##
# class AgentLogic(ABC):
#     def __init__( self, *args ):
#         self.actions = [ *args ]

#     def select_action(self, agent, surroundings=[]):
#         """
#         Select an action to perform
#         return: action, {action_params}, target_agent
#         """
#         selected_action = random.choice( self.actions ) if len(self.actions) > 0 else None
#         action_params = {}
#         target_agent = None
#         return selected_action, action_params, target_agent

#     def do_action(self, agent, surroundings=[]):
#         """
#         select and do an action
#         return: new_agent_state, new_target_agent_state, elapsed_time
#         """
#         action = self.select_action( agent, surroundings )
#         if action is None:
#             return agent.state, None, 0
#         else:
#             raise ValueError("the action needed to be defined")

#         if action is not None:
#             action.do_action(agent, target_agent)

# class PreyLogic(AgentLogic):
#     def __init__(self):
#         super().__init__( ActionMove(), ActionEat() )

# class BlockLogic(AgentLogic):
#     def __init__(self):
#         super().__init__()

#     def select_action(self, agent, surroundings=[]):
#         return None, {}, None

# ##
# ## available actions
# ##
# class Action(ABC):
#     def __init__(self, success_probability=100, time_consumption=99, parameters={} ):
#         self.success_probability = success_probability
#         self.time_consumption = time_consumption
#         self.parameters = parameters
#         self.energy_consumption = 0

#     def logic_name(self):
#         return self.__class__.__name__
    
#     def _self_effect(self, agent):
#         state = agent.state.clone()
#         state.energy -= self.energy_consumption
#         return state

#     def _target_effect(self, target_agent):
#         state = target_agent.state.clone()
#         return state

#     def solo_action(self, agent):
#         new_state = self._self_effect(agent)
#         return new_state, None, self.time_consumption

#     def pared_action(self, agent, target_agent):
#         new_t_state = self._target_effect(target_agent)
#         new_a_state = self._self_effect(agent)
#         return new_a_state, new_t_state, self.time_consumption

# class ActionMove(Action):
#     def __init__(self, success_probability=100, time_consumption=99, energy_consumption=2 ):
#         parameters = { 'length': ParamLength(), 'direction': ParamDirection() }
#         super().__init__(success_probability, time_consumption, energy_consumption, parameters)

#     def do_action(self, agent):
#         params = self.parameters
#         length = params['length'].random_choice_values()
#         direction = params['direction'].random_choice_values()
#         agent.move(length, direction)

# # class Params:
# #     def __init__(self, *args):
# #         self.params = args

# #     @abstractmethod
# #     def possible_values(self):
# #         pass

# #     @classmethod
# #     def random_choice_values(cls):
# #         return random.choice( cls.possible_values() )

# #     def params_name(self):
# #         return self.__class__.__name__

# # class ParamLength(Params):
# #     def __init__(self, *args):
# #         super().__init__(*args)

# #     def possible_values(self):
# #         return [1,2]
                
# # class ParamDirection(Params):
# #     def __init__(self, *args):
# #         super().__init__(*args)

# #     def possible_values(self):
# #         return [1,2,3,4,5,6,7,8,9]
    


# class ActionEat(Action):
#     def __init__(self, success_probability=100, time_consumption=99, energy_consumption=1 ):
#         parameters = {}
#         super().__init__(success_probability, time_consumption, energy_consumption, parameters)

#     def do_action(self, agent, target_agent):
#         agent.state.energy

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
        return f"E: {self.energy()} - {self.msg[-1:]}"

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
            else:
                raise ValueError("select_direction must be callable")
            del kwargs['select_direction']
        else:
            self.direction_selector = lambda surrounding: randint(1,9) if randint(1,10) > 7 else self.direction()

        super().__init__( **kwargs )

    def select_direction(self, surrounding=None):
        return self.direction_selector(surrounding)

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

