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
            uvalue, params = a.calculate_utility(state)
            utility_by_action[a.name] = (a,self.__limit_calculate_utility(uvalue),params)

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
        self._default_params = params
        self.success_prob = success_prob
        self.utility_base_value = utility_base_value
        self._param_key = self.__class__.__name__+'_param_key'
        self._resutl_key = self.__class__.__name__+'_result_key'

    # def get_run_params(self,state,default=None):
    #     return state.t_get_attr(self._param_key, default)
    
    # def set_run_params(self,state,params):
    #     state.t_set_attr(self._param_key, params)

    def get_action_result(self,state,default=None):
        return state.t_get_attr(self._resutl_key, default)
    
    def set_action_result(self,state,result):
        state.t_set_attr(self._resutl_key, result)

    def calculate_utility(self, state):
        """calculate the utility of the action
        return utility_value, run_action_params
        """
        return self.utility_base_value,None


    def __action_run_success(self, state):
        """calculate the success of the action
        return: True/False
        """
        res = False
        if self.success_prob == 1:
            res = True
        else:
            res = True if random() < self.success_prob else False
        state.t_set_attr('action_success_run', res)
        return res


    def action_run_success(self, state):
        """check if the action run was successful
        return: True/False/None (if not run yet)
        """
        return state.t_get_attr('action_success_run', None)


    def run_action(self, agent, state, params):
        """ **interaction phase** interface to run the action,
        return None
        """
        if self.__action_run_success(state):
            # self.set_run_params(state, params) ---- not needed call done by agent
            result = self.action_self_effect(agent, state, params)
            self.set_action_result(state, result)
        return


    def action_self_effect(self,agent,state,params):
        """
        **ovrride this method** to implement the action effect
        return result (any data type)
        """
        pass


    def action_update_phase(self,agent,state):
        """
        **update phase**
        use returned data by action_self_effect to update state
        return None
        """
        result = self.get_action_result(state)
        if( result is not None ):
            self.do_update(agent, state, result)
        return

    def do_update(self, agent, state,result):
        """
        **ovrride this method** to implement the action update phase
        update the state based on the result of the action
        return None
        """
        pass
    
    def get_action_param_value(self, state, param_name, default=None):
        """get the action parameter value from the state
        if not found, return default value
        """
        key = self.__class__.__name__ + '|' + param_name
        v = state.t_get_attr(key, None)
        if v is None:
            try:
                # v = self._default_params[self.__class__.__name__][param_name]
                v = self._default_params[param_name]
            except KeyError:
                raise ValueError(f"Parameter '{param_name}' not found in default params: {str(self._default_params)}")
        
        return v

    def get_current_state_value_for(self, state, param_name, default=None):
        """get the current state value for the parameter"""

        return state.t_get_attr(param_name, default)

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
    """
    needed parameters:
    - energy_recovery
    - max_recoverable_energy
    """
    def __init__(self, params=None, **kwargs):
        if params is  None:
            params = { 'energy_recover': 2, 'max_recoverable_energy': 25 }
        super().__init__('rest', params, **kwargs)

    def calculate_utility(self, state):
        current_energy = state.t_get_attr('energy', 0)
        if( current_energy >= self.get_action_param_value(state,'max_recoverable_energy') ):
            return 0, None
        return self.get_action_param_value(state,'energy_recover'),None
    
    def action_self_effect(self,agent, state, _):
        current_energy = state.t_get_attr('energy',0)
        new_energy = current_energy + self.get_action_param_value(state,'energy_recover')
        state.t_set_attr('energy', new_energy)
        return None

class mate(action):
    """
    needed parameters:
    - 'mate_species': [],
    - 'penalty_species': [],
    - 'penalty_count_factor': 2,
    - energy_penalty: 0

    t_attrs (via calculate_utility):
    - mate_meta_nearby: (agent, distance, direction)
    - run_params: { utility_value: x, mate_meta_nearby: (o,dist,dir) }
    """
    def __init__(self, params=None, **kwargs):
        if params is None:
            params = { 'mate_species': [],
                       'utility_value': 10,
                       'minimal_energy': 0,
                       'nearby_distance': 0,
                       'penalty_species': [],
                       'penalty_distance_factor': 0.5,
                       'penalty_count_factor': 1,
                       'energy_penalty': 0,                        
            }
        super().__init__('mate', params, **kwargs)


    def calculate_utility(self, state):
        # Get the surrounding species
        uvalue = self.utility_base_value
        run_params = None
        saw = state.saw()

        if saw is None:
            # no surrounding
            return 0, None
        
        # find same species
        same_species = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'mate_species'))
        if ( len(same_species) == 0
                or state.t_get_attr('energy',0) < self.get_action_param_value(state,'minimal_energy') ):
            # No species found in the surrounding
            return 0, None
        mate_meta_nearby = same_species[0]
        state.t_set_attr('mate_meta_nearby', mate_meta_nearby)

        if(mate_meta_nearby[1] > self.get_action_param_value(state,'nearby_distance') ):
            # too far away
            return 0, None

        # Penalty for the species in 'penalty'
        penalty_meta_agents = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'penalty_species'))
        penalty = sum( self.get_action_param_value(state,'penalty_count_factor')
                        + ( self.get_action_param_value(state,'penalty_distance_factor') * o[1] )
                        for o in penalty_meta_agents)

        uvalue += self.get_action_param_value(state,'utility_value') - penalty
        run_params = {
            'utility_value': uvalue,
            'mate_meta_nearby': mate_meta_nearby,
        }
                  
        state.t_set_attr('run_params', run_params)
        return uvalue, run_params


    def action_self_effect(self,agent,state,params):

        current_energy = self.get_current_state_value_for(state, 'energy')
        new_energy = current_energy - self.get_action_param_value(state,'energy_penalty')
        self.set_current_state_value_for(state, 'energy', new_energy)

        result_target = None
        result_new_agent = []
        # get the mate meta nearby
        mate_meta_nearby = state.t_get_attr('mate_meta_nearby', None)
        if mate_meta_nearby is not None:
            # mate is possible
            partner,dist,dir = mate_meta_nearby
            result_target = partner
            result_new_agent = agent.mate( partner = partner, mate_params = params)

        return { 'partner': result_target,
                 'new_agent': result_new_agent, }


    def do_update(self,agent,state,result):
        """update the state based on the result of the action
        return None
        """
        if result is None:
            return
        
        if 'new_agent' in result and len(result['new_agent']) > 0:
            # get the new agent
            saw = state.saw()
            empty_pos = saw.find_empty_position()
            for a in result['new_agent']:
                if len(empty_pos) == 0:
                    # no empty position
                    break
                x,y = choice(empty_pos)
                empty_pos.remove((x,y))
                agent.arena.add_to_position(x,y,a)

        return

class simple_move(action):
    """
    __init__( params = { 'distance': 1, 'energy_penalty': 2, 'change_direction_prob': 0.1}
    """
    def __init__(self, params=None, **kwargs):
        if params is  None:
            params = { 'distance': 1, 'energy_penalty': 2, 'change_direction_prob': 0.1}
        super().__init__('move', params, **kwargs)


    def calculate_utility(self, state):
        return self.utility_base_value, None


    def action_self_effect(self,agent,state,params):
        current_energy = self.get_current_state_value_for(state, 'energy')
        new_energy = current_energy - self.get_action_param_value(state,'energy_penalty')
        self.set_current_state_value_for(state, 'energy', new_energy)

        if random() < self.get_action_param_value(state,'change_direction_prob'):
            # change direction
            new_direction = choice([1,2,3,4,6,7,8,9])
            state.t_set_attr('direction', new_direction)
        state.t_set_attr('move_distance', self.get_action_param_value(state,'distance'))
        return { 'dir': state.t_get_attr('direction', None),
                 'dist': self.get_action_param_value(state,'distance'), }


    def do_update(self, agent, state, result):
        if result is not None:
            direction = result['dir']
            distance = result['dist']
            agent.move(direction=direction, distance=distance)
        return


class move(simple_move):
    pass


class eat(move):
    """
    needed parameters:
    - 'max_distance': 1
    - 'target_classes': []
    - 'energy_gain': 10
    - 'penalty_species': [],
    - 'penalty_distance_factor': 0,
    - 'penalty_count_factor': 0,

    t_attrs (via calculate_utility):
    - target: (agent, distance, direction)
    """
    def __init__(self, params=None, **kwargs):
        if params is None:
            params = { 
                'max_distance': 0,
                'target_classes': [],
                'energy_gain': 10,
            }
        super().__init__('mate', params, **kwargs)


    def calculate_utility(self, state):
        # Get the surrounding species
        uvalue = self.utility_base_value
        saw = state.saw()
        if saw is not None:
            targets = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'target_classes'))
            if len(targets) == 0:
                return -1
            target = targets[0]

            if(target[1] > self.get_action_param_value(state,'max_distance')):
                # too far away
                return -1
            
            if(target[1] <= self.get_action_param_value(state,'max_distance')):
                # expect energy gain
                gain += self.get_action_param_value(state,'energy_gain', 0)

                penalty_meta_agents = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'penalty_species'))
                penalty = sum( self.get_action_param_value(state,'penalty_count_factor')
                                + ( self.get_action_param_value(state,'penalty_distance_factor') * o[1] )
                                for o in penalty_meta_agents)
                
                uvalue += gain - penalty

                run_params = {
                    'utility_value': uvalue,
                    'energy_gain': gain,
                    'target_meta': target,
                }
            
        state.t_set_attr('run_params', run_params)
        return uvalue, run_params


    def action_self_effect(self,agent,state,params):

        current_energy = self.get_current_state_value_for(state, 'energy')
        new_energy = current_energy - params['energy_gain']
        self.set_current_state_value_for(state, 'energy', new_energy)

        return { 'target': params['target_meta'][0] }


    def do_update(self,agent,state,result):
        """update the state based on the result of the action
        return None
        """
        if result is None:
            return

        target = result['target']
        if target is not None:
            target.eaten()

        return
