from random import choice, random
from ppSlib.arena_sync_model import asmState

class action_selection():
    """class to manage action logic: utility calculation; action selection; action parameters
    How to use:

    1. create action_selection instance with actions

        selector = action.action_selection(actions=[rest_action])
    
    2. calculate utility of actions, and get the top action

        utilities = selector.calculate_utility(state=state)
        (action, utility_value) = utilities.get_top_action_list()[0]

    3. ask the action to calculate its parameters

        params = action.calculate_action_params(state=state)

    4. ask the action to apply its effect on the agent state

        action.action_self_effect(agent_state, params=params)

    """
    def __init__(self, actions=[]):
        self.actions_list = []
        for a in actions:
            if not isinstance(a, action):
                raise ValueError("action must be an instance of action class")
            self.actions_list.append(a)
    
        self.min_uvalue = 0
        self.max_uvalue = 100


    def add_action(self, naction):
        if not isinstance(naction, action):
            raise ValueError("action must be an instance of action class")
        self.actions_list.append(naction)


    def __limit_calculate_utility(self, uvalue):
        if uvalue < self.min_uvalue:
            uvalue = self.min_uvalue
        elif uvalue > self.max_uvalue:
            uvalue = self.max_uvalue
        return uvalue


    def calculate_utility(self,state):
        utility_by_action = {}
        for a in self.actions_list:
            uvalue = a.calculate_utility(state)
            utility_by_action[a.name] = (a,self.__limit_calculate_utility(uvalue))

        return action_utility_list(utility_by_action)

    # def calculate_action_params(self, action, state, chromosome=None):
    #     return action.calculate_action_params(state=state, chromosome=chromosome)

    # def action_self_effect(self, agent_state, **kwargs):
    #     return self.action.action_self_effect(agent_state)

    # def action_other_effect(self, agent_state, other_agent_state, **kwargs):
    #     return self.action.action_other_effect(agent_state, other_agent_state)

    def __str__(self):
        return f"action_selection: {self.actions_list}"

class action_utility_list():
    def __init__(self, ulist):
        self.ulist = ulist
        self._sorted_ulist = None

    def _sort_ulist(self):
        if self._sorted_ulist is None:
            self._sorted_ulist = sorted(self.ulist.values(), key=lambda x: x[1], reverse=True)

    def get_top_action_list(self, n=1):
        """return the top n actions"""
        self._sort_ulist()        
        if n > len(self._sorted_ulist):
            n = len(self._sorted_ulist)
        return self._sorted_ulist[:n]
        
    def __iter__(self):
        self._sort_ulist()
        return iter(self._sorted_ulist)

    def __len__(self):
        return len(self.ulist)
    
    def __str__(self):
        self._sort_ulist()
        return ",".join( [ str(value[0].name) +":"+ str(value[1]) for value in self._sorted_ulist] )


class action:
    def __init__(self, name, params={}, success_prob=1, utility_base_value=0 ):
        self.name = name
        self.params = params
        self.success_prob = success_prob
        self.utility_base_value = utility_base_value


    def calculate_utility(self, state):
        """calculate the utility of the action"""
        return self.utility_base_value


    def __action_run_success(self, state):
        """calculate the success of the action"""
        if self.success_prob == 1:
            return True
        else:
            return True if random() < self.success_prob else False


    def run_action(self, state):
        """run the action"""
        self.__action_run_success(state)
        return self.action_self_effect(state)


    def action_self_effect(self,state):
        pass

    
    def get_current_state_value_for(self, state, param_name):
        """get the current state value for the parameter"""

        return state.t_get_attr(param_name, None)

        # if param_name not in self.params:
        #     raise ValueError(f"Parameter {param_name} not found")
        # getter = self.params[param_name]['getter']
        # return getattr(state, getter, lambda: None)()

    def set_current_state_value_for(self, state, param_name, value):
        """set the current state value for the parameter"""
        state.t_set_attr(param_name, value)

        # if param_name not in self.params:
        #     raise ValueError(f"Parameter {param_name} not found")
        # setter = self.params[param_name]['setter']
        # if setter is None:
        #     raise ValueError(f"Setter for parameter {param_name} not found")
        # getattr(state, setter, lambda x: None)(value)

    def __str__(self):
        return f"action: {self.name} | params: {self.params} | success_prob: {self.success_prob} | utility_base_value: {self.utility_base_value}"
    def __repr__(self):
        return f"action: {self.name} | params: {self.params} | success_prob: {self.success_prob} | utility_base_value: {self.utility_base_value}"


class rest(action):
    def __init__(self, params=None, **kwargs):
        if params is  None:
            params = { 'energy_recover': 2 }
        super().__init__('rest', params, **kwargs)

    def calculate_utility(self, state):
        current_energy = state.t_get_attr('energy', 0)
        return super().calculate_utility(state) + 10 - current_energy
    
    def action_self_effect(self, state):
        current_energy = state.t_get_attr('energy',0)
        new_energy = current_energy + self.params['energy_recover']
        state.t_set_attr('energy', new_energy)
        return

class mate(action):
    def __init__(self, params=None, **kwargs):
        super().__init__('mate', params, **kwargs)
    
    def action_self_effect(self, state):
        current_energy = state.t_get_attr('energy',0)
        new_energy = current_energy + self.params['energy_recover']
        state.t_set_attr('energy', new_energy)
        return

class move(action):
    """
    __init__( params = { 'distance': 1, 'energy_penalty': 2, 'change_direction_prob': 0.1}
    """
    def __init__(self, params=None, **kwargs):
        if params is  None:
            params = { 'distance': 1, 'energy_penalty': 2, 'change_direction_prob': 0.1}
        super().__init__('move', params, **kwargs)

    
    def action_self_effect(self,state):
        current_energy = self.get_current_state_value_for(state, 'energy')
        new_energy = current_energy - self.params['energy_penalty']
        self.set_current_state_value_for(state, 'energy', new_energy)

        if random() < self.params['change_direction_prob']:
            # change direction
            new_direction = choice([1,2,3,4,6,7,8,9])
            state.t_set_attr('direction', new_direction)
        state.t_set_attr('move_distance', self.params['distance'])
        return [ state.t_get_attr('direction', None), self.params['distance'] ]

class eat(move):
    """
    __init__( params = { 'max_distance': 1, 'energy_penalty': 2, 'energy_recover': 10}
    """
    def __init__(self, params=None):
        if params is  None:
            params = { 'energy_penalty': 2, 'energy_recover': 10 }
        super().__init__('eat',params)
    
    def action_self_effect(self,state):
        ## always consume energy
        current_energy = self.get_current_state_value_for(state, 'energy')
        new_energy = current_energy - self.params['energy_penalty']
        self.set_current_state_value_for(state, 'energy', new_energy)

        ## only recover energy if the action is successful
        if self.__action_run_success(state):
            current_energy = self.get_current_state_value_for(state, 'energy')
            new_energy = current_energy - self.params['energy_recover']
            self.set_current_state_value_for(state, 'energy', new_energy)

            t = state.t_get_attr('target', None)
            if t is not None:
                ## set the target to 0
                t.t_set_attr('energy',0)

        return [ None, None]
    