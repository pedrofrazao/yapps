import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import unittest.mock
from ppSlib.agent import Agent as Agent, Block, Glide, Prey, Carnivore, Trap, LivingAgent, Grass
import ppSlib.agent as agentcls
from ppSlib.action import move, action
from ppSlib.arena_sync_model import ArenaSyncModel

debug = lambda x: print(f">> {str(x)}") if( os.environ.get('DEBUG', False) ) else None
            
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

        chromosome = [  ('rest|energy_recover',[1,5,10,20],"" ),
                        ('see_length',[2,3],"" ),
                        ('gene1',[1,2,3,4],""),
                        ('gene2',[11,12,13,14],""),
                        ('gene3',[21,22,23,24],"" ),
                        ('gene4',[31,32,33,34],"" ),
                        ('gene5',[41,42,43,44],"" ),
        ]
        alist = [] 
        alist.append( agentcls.Grass2(arena = self.arena, chromosome=chromosome) )
        alist.append( agentcls.Grass2(arena = self.arena, chromosome=chromosome) )

        self.arena.add_to_position(2, 2, alist[0])
        self.arena.add_to_position(3, 3, alist[1])

        self.alist = alist
        self.chromosome_init = chromosome

    def test_agent(self):
        debug( self.arena )
        g1 = self.alist[0]
        g2 = self.alist[1]

        r1 = g1.chromosome.gene_value('rest|energy_recover')
        r2 = g2.chromosome.gene_value('rest|energy_recover')

        self.assertIn(g1.chromosome.gene_value('see_length'), [2,3])
        self.assertIn(g2.chromosome.gene_value('see_length'), [2,3])
        self.assertIn(r1, [1,5,10,20])
        self.assertIn(r2, [1,5,10,20])
        debug( f"g1: {r1}, g2: {r2}" )

        e1 = g1.energy()
        e2 = g2.energy()
        self.assertEqual(e1, 1 )
        self.assertEqual(e2, 1 )

        self.arena.run_step()

        self.assertIn('rest', g1.get_last_msg())
        self.assertIn('rest', g2.get_last_msg())
        
        self.assertEqual(g1.energy(), e1+r1 )
        self.assertEqual(g2.energy(), e2+r2 )
        e1 += r1
        e2 += r2

        for _ in range(40):
            self.arena.run_step()
        
            if( 'mate' in g1.get_last_msg()
               or 'mate' in g2.get_last_msg() ):
                break

            self.assertIn('rest', g1.get_last_msg())
            self.assertIn('rest', g2.get_last_msg())
            self.assertEqual(g1.energy(), e1+r1 )
            self.assertEqual(g2.energy(), e2+r2 )
            e1 += r1
            e2 += r2

        # mate done
        debug( self.arena )

        ids = [g1.id, g2.id]
        new_agent = None
        for agent in self.arena.get_objects():
            if agent.id not in ids:
                new_agent = agent
                break
        debug( self.arena )

        debug(f"g1: {g1.chromosome}")
        debug(f"g2: {g2.chromosome}")
        if new_agent is None:
            breakpoint()

        debug( g1.arena.get_objects() )
        debug(f"new: {new_agent.chromosome}")

        for k,_,_ in self.chromosome_init:
            self.assertIn(new_agent.chromosome.gene_value(k), ( g1.chromosome.gene_value(k), g2.chromosome.gene_value(k) ) )
            

if __name__ == '__main__':
    unittest.main(verbosity=2)
