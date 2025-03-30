import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import action

class TestAction(unittest.TestCase):
    def setUp(self):
        self.actions_list = [ action.rest( params={'energy_recover':{"value":2, "getter": "energy", "setter":"set_energy"}} ),
                                action.move( params={'direction': {'value':0, "getter": "direction", "setter": "set_direction"},
                                            'distance': {'value':1},
                                            'energy_penalty': {'value':1, "getter": "energy", "setter": "set_energy"},
                                        }) ]

    def test_action1(self):
        self.assertEqual( len(self.actions_list), 2 )
        self.assertEqual( self.actions_list[0].name, 'rest' )
        self.assertEqual( self.actions_list[1].name, 'move' )

    def test_action_utility(self):
        # calc for rest
        rest = self.actions_list[0]
        state = astate(5)
        
        self.assertEqual( rest.calculate_utility(state), 10 - 5 )
        self.assertEqual( state.energy(), 5 )
        rest.action_self_effect(state)
        self.assertEqual( state.energy(), 7 )

        state = astate(100)
        self.assertEqual( rest.calculate_utility(state), 10 - 100 )
        rest.action_self_effect(state)
        self.assertEqual( state.energy(), 102 )

    def test_rest_action(self):
        state = astate(40)
        rest_action = action.rest()

        # Test utility calculation
        utility = rest_action.calculate_utility(state)
        assert utility == 10 - 40 + rest_action.utility_base_value

        # Test self-effect
        rest_action.action_self_effect(state)
        assert state._energy == 42  # Energy increased by 2 (default recovery value)

    def test_move_action(self):
        state = astate(50)
        move_action = action.move()

        # Test action parameters
        params = move_action.calculate_action_params()
        assert "distance" in params
        assert "direction" in params
        assert params["direction"] in [1, 2, 3, 4, 6, 7, 8, 9]

        # Test self-effect
        move_action.action_self_effect(state)
        assert state._energy == 49  # Energy decreased by 1 (default penalty value)

    def test_action_selection(self):
        state = astate(4)
        rest_action = action.rest()
        move_action = action.move()

        selector = action.action_selection(actions=[rest_action, move_action])

        # Test adding actions
        assert len(selector.actions_list) == 2

        # Test utility calculation
        utilities = selector.calculate_utility(state=state)
        assert len(utilities) == 2
        uu = [ u for u in utilities ]
        assert uu[0][0].name == 'rest'
        assert uu[1][0].name == 'move'
        assert uu[0][1] == 6
        assert uu[1][1] == 0

class TestActionList2(unittest.TestCase):
    def setUp(self):
        state = astate(4)
        rest_action = action.rest( utility_base_value=5,
                                   params={'energy_recover':{"value":10, "getter": "energy", "setter":"set_energy"}} )
        move_action = action.move( utility_base_value=8,
                                   params={'direction': {'value':0, "getter": "direction", "setter": "set_direction"},
                                           'distance': {'value':2},
                                           'energy_penalty': {'value':2, "getter": "energy", "setter": "set_energy"},
                                       })

        selector = action.action_selection(actions=[rest_action])
        selector.add_action(move_action)
        self.selector = selector
        self.state = state

    def test_action_selection2(self):
        selector = self.selector
        state = self.state

        # Test adding actions
        assert len(selector.actions_list) == 2

        # Test utility calculation
        utilities = selector.calculate_utility(state=state)
        assert len(utilities) == 2
        uu = [ u for u in utilities ]
        # print( ">> "+ str(uu) )
        assert uu[0][0].name == 'rest'
        assert uu[1][0].name == 'move'
        assert uu[0][1] == 5 + 10 - 4
        assert uu[1][1] == 8

        [a] = utilities.get_top_action_list()
        a,u = a
        assert a.name == 'rest'
        assert u == 5 + 10 - 4
        


class astate():
    def __init__(self,energy, direction=0):
        self._energy = energy
        self._direction = direction

    def energy(self):
        return self._energy
    def set_energy(self, energy):
        self._energy = energy
    def direction(self):
        return self._direction
    def set_direction(self, direction):
        self._direction = direction
    def __str__(self):
        return f"energy: {self._energy}, direction: {self._direction}"
    def __repr__(self):
        return f"energy: {self._energy}, direction: {self._direction}"


if __name__ == '__main__':
    unittest.main(verbosity=2)