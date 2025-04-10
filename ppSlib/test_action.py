import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import ppSlib.action as action
from ppSlib.agent import LivingAgent
from ppSlib.arena_sync_model import asmState

class TestAction(unittest.TestCase):
    def setUp(self):
        self.agent = LivingAgent( 'agent', state_args={}, arena=1 )
        self.actions_list = [ action.rest( params={'energy_recover':2, 'max_recoverable_energy': 25} ),
                                action.move( params={'distance':1,'energy_penalty': 2} ) ]


    def test_action1(self):
        self.assertEqual( len(self.actions_list), 2 )
        self.assertEqual( self.actions_list[0].name, 'rest' )
        self.assertEqual( self.actions_list[1].name, 'move' )

    def test_action_utility(self):
        # calc for rest
        rest = self.actions_list[0]
        state = asmState( {'energy': 5})
        
        uvalue, params = rest.calculate_utility(state)
        self.assertEqual( uvalue, 2)
        self.assertEqual( state.t_get_attr('energy',None), 5 ) 

        rest.run_action(self.agent,state, params)
        self.assertEqual( state.t_get_attr('energy',None), 5,"unchanged before update" )
        state.switch_to_next_state()
        self.assertEqual( state.t_get_attr('energy',None), 7,"+ after rest" )

        state = asmState( {'energy': 100})
        uvalue, params = rest.calculate_utility(state)
        self.assertEqual( uvalue, max(0, 10 - 100) )
        rest.run_action(self.agent, state, params)
        state.switch_to_next_state()
        self.assertEqual( state.t_get_attr('energy',None), 102 )

    def test_rest_action(self):
        state = asmState( {'energy': 40, 'max_recoverable_energy':25})
        rest_action = action.rest()

        # Test utility calculation
        utility,params = rest_action.calculate_utility(state)
        assert utility == 0

        # Test self-effect
        rest_action.run_action(self.agent,state, params)
        state.switch_to_next_state()
        self.assertEqual( state.t_get_attr('energy',None), 42, "Energy increased by 2 (default recovery value)" )

    def test_move_action(self):
        state = asmState( {'energy': 50, 'direction': 0})
        move_action = action.move({ 'distance': 1, 'energy_penalty': 2, 'change_direction_prob': 1})
        utility,params = move_action.calculate_utility(state)

        # Test self-effect
        move_action.run_action(self.agent,state,params)
        r = move_action.get_action_result(state)
        self.assertEqual(r.get('move_distance',-1), 1, "Default distance is 1")
        self.assertIn(r.get('direction',-1), [1,2,3,4,6,7,8,9], "valid direction")
        state.switch_to_next_state()
        self.assertEqual( state.t_get_attr('energy',-1),48 , "Energy decreased by 1 (default penalty value)" )
        self.assertIn(state.t_get_attr('direction',-1), [1,2,3,4,6,7,8,9])

    def test_action_selection(self):
        state = asmState( {'energy': 50, 'direction': 0})
        rest_action = action.rest()
        move_action = action.move({ 'distance': 1, 'energy_penalty': 2, 'change_direction_prob': 1, 'utility_base_value':6})

        selector = action.action_selection(actions=[rest_action, move_action])

        # Test adding actions
        assert len(selector.actions_list) == 2

        # Test utility calculation
        utilities = selector.calculate_utility(state=state)
        # print( ">> "+ str(utilities) )
        assert len(utilities) == 2
        uu = [ u for u in utilities ]
        assert uu[0][0].name == 'move'
        assert uu[1][0].name == 'rest'
        assert uu[0][1] == 6
        assert uu[1][1] == 0


class TestActionList2(unittest.TestCase):
    def setUp(self):
        self.agent = LivingAgent( 'agent', state_args={}, arena=1 )
        state = asmState( {'energy': 4})
        rest_action = action.rest( params={'energy_recover':10, 'max_recoverable_energy':11, 'utility_base_value': 0, } )
        move_action = action.move( params={'distance':2, 'energy_penalty': 2, 'change_direction_prob':0, 'utility_base_value':5} )
 
        selector = action.action_selection(actions=[rest_action])
        selector.add_action(move_action)
        self.selector = selector
        self.state = state

    def test_action_selection2(self):
        selector = self.selector
        state = self.state

        # Test adding actions
        self.assertEqual( len(selector.actions_list), 2 )

        # Test utility calculation
        utilities = selector.calculate_utility(state=state)
        self.assertEqual( len(utilities), 2 )
        uu = utilities.get_top_action_list(n=2)
        # print( ">> "+ str(uu) )
        self.assertEqual( uu[0][0].name, 'rest' )
        self.assertEqual( uu[1][0].name, 'move' )
        self.assertEqual( uu[0][1], 0 + 10 )
        self.assertEqual( uu[1][1], 5 )

        ## calc action parameters
        a = uu[0][0]
        params = uu[0][2]
        b_energy = state.t_get_attr('energy')
        a.run_action(self.agent,state,params)
        state.switch_to_next_state()
        a_energy = state.t_get_attr('energy')
        self.assertEqual( a_energy , b_energy + 10 )

        # commit results on state strucuture
        a.action_update_phase(self.agent,state)

        ## try new selection
        utilities = selector.calculate_utility(state=state)
        assert len(utilities) == 2

        # print( ">> "+ str(uu) )
        (a, u, p) = utilities.get_top_action_list()[0]
        self.assertEqual(a.name,'move')
        a.run_action(self.agent,state,p)

        self.assertEqual( state.t_get_attr('move_distance', 0), 2 )
        self.assertIn( state.t_get_attr('direction', 0), [0] )
        # print( ">> "+ str(params) )





if __name__ == '__main__':
    unittest.main(verbosity=2)