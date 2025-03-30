from random import choice


class action_selection():
    """class to manage action logic: utility calculation; action selection; action parameters"""
    def __init__(self, **kwargs):
        self.actions_list = []
        for a in kwargs.get('actions',[]):
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


    def calculate_utility(self, **kwargs):
        utility_by_action = {}
        for a in self.actions_list:
            uvalue = a.calculate_utility(**kwargs)
            utility_by_action[a.name] = (a,self.__limit_calculate_utility(uvalue))

        return action_utility_list(utility_by_action)

    def calculate_action_params(self, state, chromosome=None):
        return self.action.calculate_action_params(state, chromosome)

    def action_self_effect(self, agent_state):
        return self.action.action_self_effect(agent_state)

    def action_other_effect(self, agent_state, other_agent_state):
        return self.action.action_other_effect(agent_state, other_agent_state)

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

    def calculate_utility(self, state, **kwargs):
        """calculate the utility of the action"""
        return self.utility_base_value

    def action_self_effect(agent_state):
        return agent_state
    
    def action_other_effect(agent_state, other_agent_state):
        return other_agent_state
    
    def get_current_state_value_for(self, state, param_name):
        """get the current state value for the parameter"""
        if param_name not in self.params:
            raise ValueError(f"Parameter {param_name} not found")
        getter = self.params[param_name]['getter']
        return getattr(state, getter, lambda: None)()

    def set_current_state_value_for(self, state, param_name, value):
        """set the current state value for the parameter"""
        if param_name not in self.params:
            raise ValueError(f"Parameter {param_name} not found")
        setter = self.params[param_name]['setter']
        if setter is None:
            raise ValueError(f"Setter for parameter {param_name} not found")
        getattr(state, setter, lambda x: None)(value)

    def __str__(self):
        return f"action: {self.name} | params: {self.params} | success_prob: {self.success_prob} | utility_base_value: {self.utility_base_value}"
    def __repr__(self):
        return f"action: {self.name} | params: {self.params} | success_prob: {self.success_prob} | utility_base_value: {self.utility_base_value}"

class rest(action):
    def __init__(self, **kwargs):
        if kwargs.get('params') is  None:
            kwargs['params'] = {'energy_recover':{"value":2, "getter": "energy", "setter":"set_energy"}}
        super().__init__('rest', **kwargs )

    def calculate_utility(self, state, **kwargs):
        current_energy = self.get_current_state_value_for(state, 'energy_recover')
        return super().calculate_utility(state) + 10 - current_energy
    
    def calculate_action_params(self, **kwargs):
        return {}
    
    def action_self_effect(self, agent_state):
        current_energy = self.get_current_state_value_for(agent_state, 'energy_recover')
        new_energy = current_energy + self.params['energy_recover']['value']
        self.set_current_state_value_for(agent_state, 'energy_recover', new_energy)
        return agent_state
    

class move(action):
    def __init__(self, **kwargs):
        if kwargs.get('params') is  None:
            kwargs['params'] = { 'direction': {'value':0, "getter": "direction", "setter": "set_direction"},
                                        'distance': {'value':1, "getter": "distance"},
                                        'energy_penalty': {'value':1, "getter": "energy", "setter": "set_energy"},
                                    }
        super().__init__('move', **kwargs )

    
    def action_self_effect(self,agent_state):
        current_energy = self.get_current_state_value_for(agent_state, 'energy_penalty')
        new_energy = current_energy - self.params['energy_penalty']['value']
        self.set_current_state_value_for(agent_state, 'energy_penalty', new_energy)
        return agent_state

    def calculate_action_params(self, **kwargs):
        return {'distance': self.params['distance'], 'direction': choice([1,2,3,4,6,7,8,9])}