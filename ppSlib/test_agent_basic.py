import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import unittest.mock
from ppSlib.agent import Agent as Agent, Block, Glide, Prey, Carnivore, Trap, LivingAgent, Grass
import ppSlib.agent as agentcls
from ppSlib.action import move, action
from ppSlib.arena_sync_model import ArenaSyncModel

debug = lambda x: print(f">> {str(x)}" if( os.environ.get('DEBUG', False) ) else "")
            
class TestGlide(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')

        agent_attr = {'energy': 10, 'epoch_penalty':1, 'see_length':0, 'change_direction_prob':0}
        alist = []
        a = [move({ 'distance': 1, 'energy_penalty': 0, 'change_direction_prob': 0 })]
        alist.append( Glide( arena = self.arena, dir=1, state_args=agent_attr, actions = a ) )
        
        self.arena.add_to_position(2, 0, alist[0])
        
        self.alist = alist

    def test_glide(self):
        g1 = self.alist[0]
        debug( self.arena )
        self.assertEqual(g1.energy(), 10 )
        self.assertEqual(g1.getposition(), (2, 0) )
        self.assertEqual(g1.getsattr('age'), 0 )

        self.arena.run_step()
        
        self.assertEqual(g1.energy(), 9 )
        self.assertEqual(g1.getposition(), (1, 4) )
        self.assertEqual(g1.getsattr('age'), 1 )
        debug( self.arena )

        self.arena.run_step()
        
        self.assertEqual(g1.energy(), 8 )
        self.assertEqual(g1.getposition(), (0, 3) )
        self.assertEqual(g1.getsattr('age'), 2 )
        debug( self.arena )

class TestGlideBlock(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')

        agent_attr = {'energy': 10, 'epoch_penalty':0, 'see_length':0, 'change_direction_prob':0}
        alist = []
        a = [move({ 'distance': 1, 'energy_penalty': 0, 'change_direction_prob': 0 })]
        alist.append( Glide( arena = self.arena, dir=1, state_args=agent_attr, actions = a ) )
        alist.append( Glide( arena = self.arena, dir=1, state_args=agent_attr, actions = a ) )

        self.arena.add_to_position(2, 0, alist[0])
        self.arena.add_to_position(0, 3, alist[1])
        self.arena.add_to_position(1, 0, Block(arena = self.arena))
        self.arena.add_to_position(1, 1, Block(arena = self.arena))
        self.arena.add_to_position(1, 2, Block(arena = self.arena))
        self.arena.add_to_position(1, 3, Block(arena = self.arena))
        self.arena.add_to_position(1, 4, Block(arena = self.arena))

        self.alist = alist


    def test_glide_block(self):
        g1 = self.alist[0]
        g2 = self.alist[1]
        debug( self.arena )
        self.assertEqual(g1.energy(), 10 )
        self.assertEqual(g1.getposition(), (2, 0) )
        self.assertEqual(g2.getposition(), (0, 3) )

        self.arena.run_step()
        debug( self.arena )

        self.assertEqual(g1.energy(), 10 )
        self.assertEqual(g1.getposition(), (2, 0) )
        self.assertEqual(g2.getposition(), (4, 2) )


class TestAgentGrass(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')

        alist = [] 
        alist.append( Grass(arena = self.arena) )
        alist.append( Grass(arena = self.arena) )
        alist.append( Grass(arena = self.arena) )

        self.arena.add_to_position(2, 0, alist[0])
        self.arena.add_to_position(1, 0, alist[1])
        self.arena.add_to_position(1, 1, alist[2])

        self.alist = alist

    def test_agent(self):
        debug( self.arena )
        g1 = self.alist[0]
        self.assertEqual(g1.energy(), 1 )

        self.arena.run_step()

        self.assertEqual(g1.energy(), 3 )
        debug( self.arena )

        for _ in range(4):
            self.arena.run_step()

        self.assertEqual(g1.energy(), 11 )

        self.arena.run_step()
        self.assertEqual(g1.energy(), 11-9 )

        debug( self.arena )
        self.arena.run_step()
        debug( self.arena )


class TestGAGrass(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')

        alist = [] 
        alist.append( agentcls.Grass2(arena = self.arena) )
        alist.append( agentcls.Grass2(arena = self.arena) )

        self.arena.add_to_position(2, 2, alist[0])
        self.arena.add_to_position(3, 3, alist[1])

        self.alist = alist

    def test_agent(self):
        debug( self.arena )
        g1 = self.alist[0]
        g2 = self.alist[1]

        r1 = g1.chromosome.gene_value('rest|energy_recover')
        r2 = g2.chromosome.gene_value('rest|energy_recover')

        self.assertIn(g1.chromosome.gene_value('see_length'), [0,2])
        self.assertIn(g2.chromosome.gene_value('see_length'), [0,2])
        self.assertIn(r1, [1,5,10,20])
        self.assertIn(r2, [1,5,10,20])

        self.assertEqual(g1.energy(), 1 )
        self.assertEqual(g2.energy(), 1 )

        self.arena.run_step()

        self.assertEqual(g1.energy(), 1+r1 )
        self.assertEqual(g2.energy(), 1+r2 )
        self.assertIn('rest', g1.get_last_msg())
        self.assertIn('rest', g2.get_last_msg())



        # for _ in range(4):
        #     self.arena.run_step()

        # self.assertEqual(g1.energy(), 11 )

if __name__ == '__main__':
    unittest.main(verbosity=2)
