import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import unittest.mock
from ppSlib.agent import Agent as Agent, Block, Glide
from ppSlib.arena_sync_model import ArenaSyncModel

class TestAgent(unittest.TestCase):
    def test_basic(self):
        agent = Agent()


class TestBlock(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='Sync')
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
        g1 = Glide( dir=8, arena = self.arena )
        g2 = Glide( dir=1, arena = self.arena )
        self.arena.add_to_position(0, 2, g1)
        self.arena.add_to_position(4, 4, g2)
        self.assertIn(g1, self.arena.get_position(0, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))
        
        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(1, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))
        
        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(2, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))

        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(2, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))

        self.arena.run_step()
        self.assertIn(g1, self.arena.get_position(2, 2))
        self.assertIn(g2, self.arena.get_position(4, 4))

    # def test_block_initialization(self):
    #     agent = 
    #     self.assertEqual(agent.agent_class(), 'Block')
    #     self.assertFalse(agent.can_move)
    #     self.assertEqual(agent.volume, 100)
    #     self.assertEqual(agent.priority, 0)

    #     self.assertIsNone(agent._select_action())
    #     try:
    #         agent.run_interaction()
    #     except NotImplementedError:
    #         self.fail("run_interaction() raised NotImplementedError unexpectedly!")

    #     try:
    #         agent.run_update()
    #     except NotImplementedError:
    #         self.fail("run_update() raised NotImplementedError unexpectedly!")

# class TestPrey(unittest.TestCase):
#     def test_prey_initialization(self):
#         agent = Prey(state={'energy': 10}, priority=5)
#         self.assertEqual(agent.agent_class(), 'Prey')
#         self.assertEqual(agent.state['energy'], 10)
#         self.assertEqual(agent.priority, 5)

#         self.assertIsNotNone(agent._select_action()) 
#         try:
#             agent.run_interaction()
#         except NotImplementedError:
#             self.fail("run_interaction() raised NotImplementedError unexpectedly!")

#         try:
#             agent.run_update()
#         except NotImplementedError:
#             self.fail("run_update() raised NotImplementedError unexpectedly!")

#     def test_prey_run_interaction(self):
#         prey = Prey(state={'energy': 10})
#         prey.run_interaction()
#         # Add assertions based on the expected behavior of run_interaction

#     def test_prey_run_update(self):
#         prey = Prey(state={'energy': 10})
#         prey.run_update()
#         # Add assertions based on the expected behavior of run_update

if __name__ == '__main__':
    unittest.main()