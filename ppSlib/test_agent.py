import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import unittest.mock
from ppSlib.agent import Agent as Agent, Block, Glide, Prey, Carnivore, Trap
from ppSlib.action import move, action, mate
from ppSlib.arena_sync_model import ArenaSyncModel



class see_debug(action):
    def __init__(self, params=None, **kwargs):
        super().__init__('see_debug', params, **kwargs)
    
    def action_self_effect(self, a, state, b):
        # print(str(state))
        state.t_get_attr('surroundings')
        return

class TestSee(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')
        agent_attr = {'energy': 10, 'epoch_penalty':1, 'see_length':0, 'change_direction_prob':0}
        alist = []
        alist.append( Glide( arena = self.arena, dir=1, state_args=agent_attr ) )
        alist.append( Glide( arena = self.arena, dir=2, state_args=agent_attr ) )
        alist.append( Glide( arena = self.arena, dir=3, state_args=agent_attr ) )
        alist.append( Glide( arena = self.arena, dir=4, state_args=agent_attr ) )
        self.arena.add_to_position(2, 0, alist[0])
        self.arena.add_to_position(2, 1, alist[1])
        self.arena.add_to_position(2, 2, alist[2])
        self.arena.add_to_position(2, 3, alist[3])

        self.alist = alist


    def test_see0(self):
        a_attr = {'energy': 10, 'epoch_penalty':1, 'see_length':0, 'change_direction_prob':0}
        a1 = Glide( arena = self.arena, dir=1, state_args=a_attr )
        self.arena.add_to_position(2, 1, a1)

        a1.run_interaction()
        self.assertEqual( a1.get_state().t_get_attr('surroundings').length, 0, "expected see_length" )
        saw = a1.get_state().t_get_attr('surroundings').objects
        self.assertEqual(len(saw), 1 )
        self.assertIn(self.alist[1], saw )
        

    def test_see1(self):
        a_attr = {'energy': 10, 'epoch_penalty':1, 'see_length':1, 'change_direction_prob':0}
        a1 = Glide( arena = self.arena, dir=1, state_args=a_attr )
        self.arena.add_to_position(2, 1, a1)

        a1.run_interaction()
        self.assertEqual( a1.get_state().t_get_attr('surroundings').length, 1, "expected see_length" )
        saw = a1.get_state().t_get_attr('surroundings').objects
        self.assertEqual(len(saw), 3 )
        self.assertIn(self.alist[1], saw )
        self.assertIn(self.alist[0], saw )
        self.assertIn(self.alist[2], saw )

class TestBlock(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')
        self.b1 = Block( arena = self.arena )
        self.b2 = Block( arena = self.arena )
        self.b3 = Block( arena = self.arena )
        self.b4 = Block( arena = self.arena )
        self.b5 = Block( arena = self.arena )
        self.arena.add_to_position(3, 0, self.b1)
        self.arena.add_to_position(3, 1, self.b2)
        self.arena.add_to_position(3, 2, self.b3)
        self.arena.add_to_position(3, 3, self.b4)
        self.arena.add_to_position(3, 4, self.b5)

    def test_block(self):
        g1 = Glide( dir=8, arena = self.arena, state_args={'energy': 10, 'epoch_penalty':1, 'change_direction_prob': 0} )
        g2 = Glide( dir=1, arena = self.arena, state_args={'energy': 10, 'epoch_penalty':1, 'change_direction_prob': 0} )
        self.arena.add_to_position(0, 2, g1)
        self.arena.add_to_position(4, 4, g2)
        if( os.environ.get('DEBUG', False) ):
            print(g1._action_selector)
            print(g2._action_selector)

        self.assertIn(g1, self.arena.get_position(0, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))
        self.assertEqual(g1.energy(), 10)
        self.assertEqual(g2.energy(), 10)

        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(1, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))
        self.assertEqual(g1.energy(), 9)

        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(2, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))
        self.assertEqual(g2.energy(), 8)

        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(2, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))

        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(2, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))
        self.assertEqual(g1.energy(), 6)
        self.assertEqual(g2.energy(), 6)

class TestPrey(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5)

    def test_prey(self):
        pa = [ move( { 'distance': 1, 'energy_penalty': 2, 'change_direction_prob': 0} )]
        p1 = Glide( arena = self.arena, dir=1, state_args={'energy': 10, 'epoch_penalty':1, 'see_length':0 }, actions = pa )
        g1 = Glide( arena = self.arena, dir=6, state_args={'energy': 10, 'epoch_penalty':1, 'change_direction_prob':0} )
        self.arena.add_to_position(0, 0, p1)
        self.arena.add_to_position(0, 0, g1)
        if( os.environ.get('DEBUG', False) ):
            print(self.arena)
            print(g1._action_selector)

        # see
        saw = [ i[0] for i in p1.see() ]
        self.assertIn(g1, saw )
        if( os.environ.get('DEBUG', False) ):
            print( f"{str(p1)} saw >> { ",".join([ str(i) for i in saw ]) }" )

        # test energy
        self.assertEqual(p1.energy(), 10)
        self.assertEqual(g1.energy(), 10)

        # test movement
        self.arena.run_step()
        if( os.environ.get('DEBUG', False) ):
            print(self.arena)
            print( str(p1.see()) )
        if( p1.direction() == 5 ):
            self.assertIn(p1, self.arena.get_position(0,0))
        else:
            self.assertNotIn(p1, self.arena.get_position(0,0))
        self.assertIn(g1, self.arena.get_position(0,1))
        self.assertEqual(p1.energy(),7)
        self.assertEqual(g1.energy(),9)

        # see
        saw = [ i[0] for i in p1.see() ]
        try:
            self.assertNotIn(g1, saw )
        except AssertionError as e:
            print(f"{str(p1)} saw >> { ",".join([ str(i) for i in saw ]) }")
            print(str(self.arena))
            print(g1._action_selector)
            breakpoint()
            p1.see()
            raise e
        
# class TestMate(unittest.TestCase):
#     def setUp(self):
#         self.arena = ArenaSyncModel(5, 5)
#         actions = [ mate()]
#         self.p1 = Prey( arena = self.arena, dir=1, state_args={'energy': 10, 'epoch_penalty':1, 'see_length':1 }, actions = actions )
#         self.p2 = Prey( arena = self.arena, dir=2, state_args={'energy': 10, 'epoch_penalty':1, 'see_length':1 }, actions = actions )
#         self.arena.add_to_position(0, 0, self.p1)
#         self.arena.add_to_position(0, 1, self.p2)

#     def test_mate(self):
#         # see
#         saw = [ i[0] for i in self.p1.see() ]
#         self.assertIn(self.p1, saw )
#         self.assertIn(self.p2, saw )

#         # test energy
#         self.assertEqual(self.p1.energy(), 10)
#         self.assertEqual(self.p2.energy(), 10)

#         # test mate
#         self.arena.run_step()
#         if( os.environ.get('DEBUG', False) ):
#             print(self.arena)
#             print( str(self.p1.see()) )

# class AmoveX(Agent):
#     def __init__(self, dir):
#         self.dir = dir
#     def select_action(self, state, surroundings):
#         action, action_args = super().select_action(state, surroundings)
#         if( action == 'move' ):
#             return 'move', {'direction': self.dir}
#         return action, action_args

# class PreyX(AmoveX, Prey):
#     def __init__(self, **kwargs):
#         AmoveX.__init__(self, kwargs.get('dir', 5))
#         kwargs.pop('dir', None)
#         Prey.__init__(self, **kwargs)

#     def die(self):
#         super().die()

# class CarnivoreX(AmoveX,Carnivore):
#     def __init__(self, **kwargs):
#         AmoveX.__init__(self, kwargs.get('dir', 5))
#         kwargs.pop('dir', None)
#         Carnivore.__init__(self, **kwargs)

# class TestTrap(unittest.TestCase):
#     def setUp(self):
#         self.arena = ArenaSyncModel(3, 3, sync_model='Sync')
#         self.t = Trap( arena = self.arena )
#         self.arena.add_to_position(1, 0, self.t)
#         self.p = PreyX( dir=4, arena = self.arena, state_args={'energy': 10})
#         self.arena.add_to_position(1, 2, self.p)

#     def test_trap(self):
#         self.assertIn(self.t, self.arena.get_position(1, 0))
#         self.assertIn(self.p, self.arena.get_position(1, 2))

#         self.arena.run_step()
#         self.assertIn(self.t, self.arena.get_position(1, 0))
#         self.assertIn(self.p, self.arena.get_position(1, 1))

#         self.arena.run_step()
#         self.assertIn(self.t, self.arena.get_position(1, 0))
#         self.assertIn(self.p, self.arena.get_position(1, 0))

#         self.arena.run_step()
#         self.assertIn(self.t, self.arena.get_position(1, 0))
#         self.assertNotIn(self.p, self.arena.get_position(1, 0))


# class TestPredator(unittest.TestCase):
#     def setUp(self):
#         self.arena = ArenaSyncModel(5, 5, sync_model='Sync')

#     def test_predator(self):
#         p1 = PreyX( dir=6, arena = self.arena, state_args={'energy': 10} )
#         self.arena.add_to_position(0, 0, p1)
#         c1 = CarnivoreX( dir=5, arena = self.arena, state_args={'energy': 10}, see_length=1 )
#         self.arena.add_to_position(0, 3, c1)
#         # print(self.arena)
#         #  P5 __ __ C5 __
#         #  __ __ __ __ __
#         #  __ __ __ __ __
#         #  B4 Ba Ba B0 Bb
#         #  __ __ __ __ __

#         self.arena.run_step()
#         # print(self.arena)
#         #  __ P5 __ C5 __
#         #  __ __ __ __ __
#         #  __ __ __ __ __
#         #  B4 Ba Ba B0 Bb
#         #  __ __ __ __ __
#         self.assertIn(p1, self.arena.get_position(0,1))
#         self.assertIn(c1, self.arena.get_position(0,3))
#         self.assertEqual(c1.energy(), 9)

#         self.arena.run_step()
#         # print(self.arena)
#         #  __ __ P5 C5 __
#         #  __ __ __ __ __
#         #  __ __ __ __ __
#         #  B4 Ba Ba B0 Bb
#         #  __ __ __ __ __
#         self.assertIn(p1, self.arena.get_position(0,2))
#         self.assertIn(c1, self.arena.get_position(0,3))
#         self.assertEqual(c1.energy(), 8)

#         self.arena.run_step()
#         # print(self.arena)
#         #  __ __ C5 __ __
#         #  __ __ __ __ __
#         #  __ __ __ __ __
#         #  B4 Ba Ba B0 Bb
#         #  __ __ __ __ __
#         self.assertNotIn(p1, self.arena.get_position(0,2))
#         self.assertNotIn(p1, self.arena.get_position(0,3))
#         self.assertIn(c1, self.arena.get_position(0,2))
#         self.assertEqual(c1.energy(), 17)


if __name__ == '__main__':
    unittest.main(verbosity=2)
