from random import choice, random
from ppSlib.arena_sync_model import asmState
from ppSlib.agent_direction_selector import random_direction_selector


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

        self._reorder_actions()


    def _reorder_actions(self):
        "order the action by the order value"
        self.actions_list = sorted(self.actions_list, key=lambda x: x._order_value, reverse=False)


    def add_action(self, naction):
        if not isinstance(naction, action):
            raise ValueError("action must be an instance of action class")
        self.actions_list.append(naction)
        self._reorder_actions()


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
            if uvalue < self.min_uvalue:
                # action not available
                continue
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


class action():

    def __init__(self, name, params=None, success_prob=1, order_value=25 ):
        self.params = self.get_dict_with_default_values_for_params()
        if params is not None:
            # replace default values with params
            self.params.update( params )

        self.name = name if name is not None else self.__class__.__name__
        self._default_params = params
        self.success_prob = success_prob
        # utility_base_value is stored on the params
        # self.utility_base_value = utility_base_value
        self._param_key = self.__class__.__name__+'_param_key'
        self._result_key = self.__class__.__name__+'_result_key'
        self._order_value = order_value

    def utility_base_value(self,state):
        """return the base utility value of the action"""
        return self.get_action_param_value(state,'utility_base_value',0)

    def get_dict_with_default_values_for_params(self):
        params = {key: value[0] if isinstance(value, tuple) else value 
            for key, value in self.get_action_params().items()}
        return params

    # def get_run_params(self,state,default=None):
    #     return state.t_get_attr(self._param_key, default)
    
    # def set_run_params(self,state,params):
    #     state.t_set_attr(self._param_key, params)

    def get_action_result(self,state,default=None):
        return state.t_get_attr(self._result_key, default)
    
    def set_action_result(self,state,result):
        state.t_set_attr(self._result_key, result)

    def calculate_utility(self, state):
        """calculate the utility of the action
        return utility_value, run_action_params
        """
        return self.utility_base_value(state),None


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
        if not found, return action value
        """
        key = self.__class__.__name__ + '|' + param_name
        return state.t_get_attr(key, self.params.get(param_name,self.params.get(param_name,default)) )


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

    @classmethod
    def get_available_actions(cls):
        """Returns a list of all available action subclasses."""
        return [subclass.__name__ for subclass in cls.__subclasses__()]

    # @classmethod
    # def get_action_params(cls):
    #     """Returns a dictionary of the parameters available for this action."""
    #     return cls._default_params if hasattr(cls, '_default_params') else {}


    def get_request_move(self, state):
        """return the request move parameters"""
        return state.t_get_attr('request_move', { 'meta': (None,None,None), 'utility':-1} )


    def request_move(self, state, meta, utility):
        """request a move to the given object"""
        return self.request_move_dir(state, meta[2], utility)


    def request_move_dir(self, state, direction, utility):
        """request a move in a direction"""
        if self.get_request_move(state)['utility'] > utility:
            # not enough utility
            return
        
        state.t_set_attr('request_move', { 'meta': (None, None, direction), 'utility': utility} )
        return


    def __str__(self):
        return f"action: {self.name}"
    def __repr__(self):
        return f"action: {self.name} | params: {self.params} | success_prob: {self.success_prob}"


class rest(action):
    """
    needed parameters:
    - energy_recovery
    - max_recoverable_energy
    """
    def __init__(self, params=None, **kwargs):
        super().__init__('rest', params, **kwargs)

    @classmethod
    def get_action_params(cls):
        return {'energy_recover': (2, 'Amount of energy recovered per step'),
                'max_recoverable_energy': (25, 'Maximum energy that can be recovered')}

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
    

# class mate_plus(mate):
#     @classmethod
#     def get_action_params(cls):
#         return {
#             'utility_base_value': (1, 'Base utility value for mating'),

#             'mate_species': ([], 'List of species eligible for mating'),
#             'nearby_distance': (1, 'Maximum distance to consider a mate nearby'),

#             'energy_penalty': (0, 'Energy cost of mating'),
#             'minimal_energy': (0, 'Minimum energy required to mate'),
#             'minimal_age': (0, 'Minimum age required to mate'),

#             'crossing_count': (1, 'Number of crossing points for mating'),
#             'mutation_rate': (0, 'Mutation rate for mating'),

                
#         }


#     def calculate_utility(self, state):
#         """calculate the utility of the action
#         return utility_value, run_action_params
#         """
#         if self.mate_available(state) is False:
#             return -1, None

#         # Get the surrounding species
#         saw = state.saw()

#         if saw is None:
#             # no surrounding -> no utility
#             return -1, None
        
#         # find mate species
#         same_species = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'mate_species'))
#         mate_nearby_meta = None
#         for mmn in same_species:
#             if( mmn[0].mate_available() ):
#                 mate_nearby_meta = mmn
#                 break

#         if mate_nearby_meta is None:
#             # No mate found in the surrounding
#             return -1, None
#         # one target found
#         state.t_set_attr('mate_meta_nearby', mate_nearby_meta)



class mate(action):
    """
    needed parameters:
    - 'mate_species': [],
    - 'penalty_species': [],
    - 'penalty_count_factor': 2,
    - energy_penalty: 0

    t_attrs (via calculate_utility):
    - mate_meta_nearby: (agent, distance, direction)
    - run_params: { utility_base_value: x, mate_meta_nearby: (o,dist,dir) }
    """
    def __init__(self, params=None, **kwargs):
        super().__init__('mate', params, **kwargs)

    @classmethod
    def get_action_params(cls):
        return {'mate_species': ([], 'List of species eligible for mating'),
                'penalty_species': ([], 'List of species that impose penalties'),
                'penalty_count_factor': (1, 'Penalty multiplier for the count of penalty species'),
                'penalty_distance_factor': (1, 'Penalty multiplier for the distance of penalty species'),
                'energy_penalty': (0, 'Energy cost of mating'),
                'utility_base_value': (10, 'Base utility value for mating'),
                'minimal_energy': (0, 'Minimum energy required to mate'),
                'nearby_distance': (0, 'Maximum distance to consider a mate nearby'),
                'minimal_age': (0, 'Minimum age required to mate'),
                'crossing_count': (1, 'Number of crossing points for mating'),
                'mutation_rate': (0, 'Mutation rate for mating'),
                }

    def mate_available(self, state):
        """check if mating is available
        return True/False
        """
        if state.mate_marker():
            # already marked for mating
            return False

        if state.t_get_attr('age',0) < self.get_action_param_value(state,'minimal_age',0):
            # not enough age
            return False

        if state.t_get_attr('energy',0) < self.get_action_param_value(state,'minimal_energy',0):
            # not enough energy
            return False

        return True


    def calculate_utility(self, state):
        """calculate the utility of the action
        return utility_value, run_action_params
        """
        if self.mate_available(state) is False:
            return -1, None

        # Get the surrounding species
        uvalue = self.get_action_param_value(state,'utility_base_value')
        run_params = None
        saw = state.saw()

        if saw is None:
            # no surrounding -> no utility
            return -1, None
        
        # find same species
        same_species = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'mate_species'))
        mate_meta_nearby = None
        for mmn in same_species:
            if( mmn[0].mate_available() ):
                mate_meta_nearby = mmn
                break

        if mate_meta_nearby is None:
            # No mate found in the surrounding
            return -1, None
        # one target found
        state.t_set_attr('mate_meta_nearby', mate_meta_nearby)

        request_move = False
        if(mate_meta_nearby[1] > self.get_action_param_value(state,'nearby_distance') ):
            # too far away, request move
            request_move = True

        # Penalty for the species in 'penalty'
        penalty_meta_agents = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'penalty_species'))
        penalty = sum( calc_utility_inv_square_law( o[1], self.get_action_param_value(state,'penalty_count_factor'),
                        self.get_action_param_value(state,'penalty_distance_factor') )
                        for o in penalty_meta_agents)

        uvalue -= penalty
        run_params = {
            'utility_value': uvalue,
            'mate_meta_nearby': mate_meta_nearby,
            'mutation_rate': self.get_action_param_value(state,'mutation_rate'),
            'crossing_count': self.get_action_param_value(state,'crossing_count'),
        }

        if request_move:
            self.request_move(state, mate_meta_nearby, uvalue)
            return -1, None
        else:
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
        
        # get the partner
        partner = result.get('partner', None)
        if partner is not None:
            # mate done, mark both as mated
            partner.mate_marker(True)
            agent.mate_marker(True)

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
        # the order value is used to sort the actions, and for the move the be after action that need to request a move
        super().__init__('move', params, order_value=75, **kwargs)


    @classmethod
    def get_action_params(cls):
        return { 'distance': (1,'Distance to move in a single step'),
                 'energy_penalty': (0,'Energy cost of moving'),
                 'change_direction_prob': (0.1,'Probability of changing direction during movement'),
                  'fail_re_dir': (True,'allow change dir if move fail') }

    def calculate_utility(self, state):
        req = self.get_request_move(state)
        (_,ds,dr) = req['meta']
        utility = req['utility']
        # force the distance that is used for the move
        ds = self.get_action_param_value(state,'distance',0)
        
        if( utility > self.utility_base_value(state) and dr != 5
           and dr != state.t_set_attr('fail_move_dir', None) ):
            # to avoid the move in the same failed direction
            # request move is better than the base utility
            return utility, { 'direction': dr, 'move_distance': ds }
        else:
            return self.utility_base_value(state), None


    def action_self_effect(self,agent,state,params):
        current_energy = self.get_current_state_value_for(state, 'energy')
        new_energy = current_energy - self.get_action_param_value(state,'energy_penalty')
        self.set_current_state_value_for(state, 'energy', new_energy)

        if params is not None:
            # already defined move
            return params

        distance = self.get_action_param_value(state,'distance')
        # get the current direction
        new_direction = state.t_get_attr('direction', None)
        if( ( new_direction == state.t_get_attr('fail_move_dir' ) and state.t_get_attr( 'fail_re_dir' ) )
           or random() < self.get_action_param_value(state,'change_direction_prob') ):
            # change direction
            new_direction = random_direction_selector(curr_dir=new_direction, prob_change=1)
        
        state.t_set_attr('direction', new_direction)
        state.t_set_attr('move_distance', distance)
        return { 'direction': new_direction, 'move_distance': distance }


    def do_update(self, agent, state, result):
        if result is not None:
            state.t_set_attr('direction', result['direction'])
            direction = result['direction']
            distance = result['move_distance']
            move_result = agent.move(direction=direction, distance=distance)
            if move_result is False:
                # no move done
                state.t_set_attr('fail_move_dir', result['direction'], tick_validity=1)
        return


class move(simple_move):
    pass


class escape(action):
    """
    needed parameters:
    - from_species: []
    - from_count_factor: 1
    - from_distance_factor: 1
    - to_species: []
    - to_count_factor: 1
    - to_distance_factor: 1
    """
    def __init__(self, params=None, **kwargs):
        super().__init__('escape', params, **kwargs)
    
    @classmethod
    def get_action_params(cls):
        return {'from_species': ([], 'List of species'),
                'from_count_factor': (1, 'Penalty multiplier for the count of from species'),
                'from_distance_factor': (1, 'Penalty multiplier for the distance of from species'),
                'to_species': ([], 'List of species'),
                'to_count_factor': (1, 'Penalty multiplier for the count of to species'),
                'to_distance_factor': (1, 'Penalty multiplier for the distance of to species'),
                'utility_base_value': (0, 'Base utility value for escape'),
        }

    def calculate_utility(self, state):
        # Get the surrounding species
        uvalue = self.utility_base_value(state)
        run_params = None
        saw = state.saw()

        if saw is None:
            # no surrounding -> no utility
            return -1, None
        
        # find same species
        from_species = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'from_species'))
        to_species = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'to_species'))
        if len(from_species) == 0 and len(to_species) == 0:
            return -1, None

        # one target found
        from_target = from_species[0] if len(from_species) > 0 else None
        to_target = to_species[0] if len(to_species) > 0 else None

        # Penalty for the species in 'from'
        utility_from = sum( calc_utility_inv_square_law( o[1],
                                                        self.get_action_param_value(state,'from_count_factor'),
                                                        self.get_action_param_value(state,'from_distance_factor') )
                        for o in from_species)

        # Penalty for the species in 'to'
        utility_to = sum( calc_utility_inv_square_law( o[1],
                                                      self.get_action_param_value(state,'to_count_factor'),
                                                      self.get_action_param_value(state,'to_distance_factor') )
                        for o in to_species)
        
        if( utility_from >= utility_to ):
            uvalue += utility_from
            direction = opposite_direction_to(from_target[2])
        else:
            uvalue += utility_to
            direction = to_target[2] if len(to_species)>0 else random_direction_selector(prob_change=1)

        self.request_move_dir(state, direction, uvalue)
        return -1, None


class eat(action):
    """
    needed parameters:
    - 'max_distance': 1
    - 'target_classes': []
    - 'energy_gain': 10
    - 'penalty_species': [],
    - 'penalty_distance_factor': 0,
    - 'penalty_count_factor': 0,
    - 'max_energy': 100

    t_attrs (via calculate_utility):
    - target: (agent, distance, direction)
    """
    def __init__(self, params=None, **kwargs):

        # values to init simples_move action
        # kwargs['change_direction_prob'] = 0
        # kwargs['distance'] = kwargs.get('max_distance')
        # kwargs['energy_penalty'] = 0
        super().__init__('eat', params, **kwargs)

    @classmethod
    def get_action_params(cls):
        return { 'max_distance': (0,'Maximum distance to target for eating'),
                 'target_classes': ([],'List of target classes eligible for eating'),
                 'energy_gain': (5,'Energy gained from eating a target'),
                 'penalty_species': ([],'List of species that impose penalties'),
                 'penalty_distance_factor': (1,'Penalty multiplier for the distance of penalty species'),
                 'penalty_count_factor': (1,'Penalty multiplier for the count of penalty species'),
                  'max_energy': (100,'Agent maximum energy'),}


    def calculate_utility(self, state):
        current_energy = self.get_current_state_value_for(state, 'energy')
        max_energy = self.get_action_param_value(state,'max_energy')

        if( current_energy >= max_energy ):
            return -1, None
        
        # Get the surrounding species
        uvalue = self.utility_base_value(state)
        run_params = None
        saw = state.saw()

        if saw is None:
            # no surrounding -> no utility
            return -1, None
        
        # find same species
        targets = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'target_classes'))
        if len(targets) == 0:
            return -1, None
        target = targets[0]

        request_move = False
        if(target[1] > self.get_action_param_value(state,'max_distance')):
            # too far away, request move
            request_move = True
        
        # expect energy gain
        gain = self.get_action_param_value(state,'energy_gain', 0)
        
        # Penalty for the species in 'penalty'
        penalty_meta_agents = saw.get_objects_plus_meta(only_class=self.get_action_param_value(state,'penalty_species'))
        penalty = sum( calc_utility_inv_square_law( o[1],
                                                   self.get_action_param_value(state,'penalty_count_factor'),
                                                   self.get_action_param_value(state,'penalty_distance_factor') )
                        for o in penalty_meta_agents)
        
        gain -= penalty
        gain = gain if current_energy + gain <= max_energy else max_energy - current_energy

        uvalue += gain

        if( uvalue < 0 ):
            # not enough utility
            return -1, None

        run_params = {
            'utility_value': uvalue,
            'energy_gain': gain,
            'target_meta': target,
        }

        if request_move:
            self.request_move(state, target, uvalue)
            return -1, None
        else:
            return uvalue, run_params


    def action_self_effect(self,agent,state,params):

        current_energy = self.get_current_state_value_for(state, 'energy')
        new_energy = current_energy + params['energy_gain']
        self.set_current_state_value_for(state, 'energy', new_energy)

        return { 'target': params['target_meta'][0],
                 'direction': params['target_meta'][2],
                 'move_distance': self.get_action_param_value(state,'distance') }


    def do_update(self,agent,state,result):
        """update the state based on the result of the action
        return None
        """
        if result is None:
            return

        target = result['target']
        if target is not None:
            target.eaten()

        # super().do_update(agent, state, result)
        return


def opposite_direction_to(direction):
    """return the oposite direction to the given direction
    """
    if direction == None:
        return None

    d = {1:9, 2:8, 3:7, 4:6, 5:None, 6:4, 7:3,8:2,9:1}[direction]
    if d is None:
        d = random_direction_selector(prob_change=1)

    return d


def calc_utility_inv_square_law(distance, base_utility, scaling_factor=1):
    return base_utility / (1 + scaling_factor * distance**2)