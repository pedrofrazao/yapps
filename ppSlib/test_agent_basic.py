import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import unittest.mock
from ppSlib.agent import Agent as Agent, Block, Glide, LivingAgent, Grass
import ppSlib.agent as agentcls
from ppSlib.action import move, action
import ppSlib.action as actioncls
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
        self.assertEqual(g1.age(), 2 )
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

        # force some actions configuration
        a = [actioncls.rest({ 'energy_recover': 2, 'max_recoverable_energy': 25 }),
             actioncls.mate(
               {'mate_species': ['Grass'],
                'penalty_species': [],
                'penalty_count_factor': 1,
                'penalty_distance_factor': 0.5,
                'energy_penalty': 5,
                'utility_base_value': 10,
                'minimal_energy': 10,
                'nearby_distance': 1,
               })
        ]

        alist = [] 
        alist.append( Grass(arena = self.arena, state_args={'energy':2}, actions = a) )
        alist.append( Grass(arena = self.arena, state_args={'energy':2}, actions = a) )
        alist.append( Grass(arena = self.arena, state_args={'energy':2}, actions = a) )

        self.arena.add_to_position(2, 0, alist[0])
        self.arena.add_to_position(1, 0, alist[1])
        self.arena.add_to_position(1, 1, alist[2])

        self.alist = alist

    def test_agent(self):
        self.assertEqual( self.arena.type, 'torus' )
        debug( self.arena )
        g1 = self.alist[0]
        self.assertEqual(g1.energy(), 2 )

        # should select rest action
        expected_energy = 2+2
        self.arena.run_step()
        debug( self.arena )
        self.assertEqual(g1.energy(), expected_energy )
        self.assertEqual(self.alist[1].energy(), expected_energy )
        self.assertEqual(self.alist[2].energy(), expected_energy )

        for _ in range(3):        
            # should select rest action
            expected_energy += 2
            self.arena.run_step()
            self.assertEqual(g1.energy(), expected_energy )
            self.assertEqual(self.alist[1].energy(), expected_energy )
            self.assertEqual(self.alist[2].energy(), expected_energy )
        
        # should select mate action
        self.arena.run_step()
        debug( self.arena )
        mate_count = 0
        for a in self.alist:
            debug( f"{a.nickname} {a.get_last_msg()}" )
            if( 'mate' in a.get_last_msg() ):
                mate_count += 1
                self.assertEqual(a.energy(), expected_energy - 5 )
            else:
                self.assertEqual(a.energy(), expected_energy + 2 )
        self.assertEqual(mate_count, 1)

        return
    

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

        agent_mainclass = getattr(agentcls, 'LivingGAAgent')
        agent_class = type('GrassGA', (agent_mainclass,), {})

        attr = { 'volume':1, 'energy':1,
                'epoch_penalty': 0,'see_length':1,
                'min_matetime': 5,
                }

        actions = [ 
            getattr(actioncls, 'mate')( { 'mate_species': ['GrassGA'],
                                                        'utility_base_value': 10,
                                                        'minimal_energy': 10,
                                                        'nearby_distance': 1,
                                                        'penalty_species': [],
                                                        'penalty_count_factor': 0,
                                                        'penalty_distance_factor': 0,
                                                        'energy_penalty': 9, } ),
            getattr(actioncls, 'rest')({ 'energy_recover': 2, 'max_recoverable_energy': 20 } ),
        ]

        alist = [] 
        for _ in range(2):
            alist.append( agent_class(arena=self.arena, state_args=attr, priority=5,
                                actions = actions,
                                chromosome=chromosome ) )

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


class TestAgentGrassRB(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')

        # force some actions configuration
        alist = [] 
        alist.append( Grass(arena = self.arena, state_args={'rebirth':True, 'energy':2, 'nostats': False, 'epoch_penalty':3 }) )

        self.arena.add_to_position(2, 0, alist[0])
        self.alist = alist

    def test_agent(self):
        debug( self.arena )
        g1 = self.alist[0]
        self.assertEqual(g1.energy(), 2 )

        # should select rest action
        self.arena.run_step()
        debug( self.arena )
        self.assertEqual(g1.energy(), 1 )
        self.assertEqual(g1.nostats, False )
        c = self.arena.get_count_by_object_type()
        self.assertEqual(c['Grass'],1)
        self.assertIn(g1, self.arena.get_objects())

        self.arena.run_step()
        debug( self.arena )
        l = self.arena.get_objects()
        self.assertNotIn(g1, l)
        self.assertEqual(c['Grass'],1)
        self.assertEqual(l[0].nostats, False )

        return


class TestMoving1(unittest.TestCase):
    def setUp(self):

        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')
        #  __ __ __ __ __
        #  __ __ Gx __ __
        #  __ __ __ __ __
        #  B4 Ba Ba B0 Bb
        #  __ __ __ __ __
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


        agent_attr = {'energy': 10, 'epoch_penalty':0, 'see_length':0}
        a = [move({ 'distance': 1, 'energy_penalty': 0, 'change_direction_prob': 0 })]
        g1 = Glide( arena = self.arena, dir=8, state_args=agent_attr, actions = a )
                
        self.arena.add_to_position(1, 2, g1)
        self.g1 = g1


    def test_glide_move_fail(self):
        g1 = self.g1
        debug( self.arena )
        self.assertEqual(g1.getposition(), (1, 2) )
        self.assertEqual(g1.direction(), 8 )

        self.arena.run_step()

        debug( self.arena )
        self.assertEqual(g1.getposition(), (2, 2) )
        self.assertEqual(g1.direction(), 8 )
        self.assertIsNone(g1.asmstate.t_get_attr('fail_move_dir',None))

        self.arena.run_step()

        debug( self.arena )
        self.assertEqual(g1.getposition(), (2, 2) )
        self.assertEqual(g1.direction(), 8 )
        self.assertEqual(g1.asmstate.t_get_attr('fail_move_dir',None),8)

        self.arena.run_step()
        self.assertNotEqual(g1.direction(), 8 )
        debug( self.arena )


class TestMoving2(unittest.TestCase):
    def setUp(self):

        self.arena = ArenaSyncModel(5, 5, sync_model='OASCycl')
        #  __ __ __ __ __
        #  __ __ __ __ __
        #  __ __ Rx __ __
        #  B4 Ba Ba B0 Bb
        #  __ __ Cx __ __
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

        LAgent_class = getattr(agentcls, 'LivingAgent')

        ## Cx
        cx = type('cc', (LAgent_class,), {})

        attr = { 'volume':1, 'energy':1, 'epoch_penalty': 0,'see_length':0, }
        self.cx = cx( arena = self.arena, state_args=attr, priority=5 )

        self.arena.add_to_position(4, 2, self.cx)

        ## Rx agent
        actions = [ 
            getattr(actioncls, 'eat')( { 'target_classes': ['cx'],
                                        'max_distance': 0,
                                        'energy_gain': 6,
                                        'max_energy': 100,
            } ),
            getattr(actioncls, 'move')( {'utility_base_value':1,'distance': 1, 'energy_penalty': 0, 'change_direction_prob': 0 }),
        ]

        rx = type('rx', (LAgent_class,), {})
        attr = { 'volume':1, 'energy':1, 'epoch_penalty': 0,'see_length':2, 'direction': 8 }
        self.rx = rx( arena = self.arena, state_args=attr, priority=5, actions=actions )
        self.arena.add_to_position(2, 2, self.rx)


    def test_glide_move_fail(self):
        debug( self.arena )
        # check agents positions
        self.assertEqual(self.cx.getposition(), (4, 2) )
        self.assertEqual(self.rx.getposition(), (2, 2) )
        self.assertEqual(self.rx.direction(), 8 )
        self.assertIsNone(self.rx.asmstate.t_get_attr('fail_move_dir',None))

        self.arena.run_step()
        debug( self.arena )
        self.assertEqual(self.rx.getposition(), (2, 2) )
        self.assertEqual(self.rx.direction(), 8 )
        self.assertEqual(self.rx.asmstate.t_get_attr('fail_move_dir',None), 8)

        self.arena.run_step()
        debug( self.arena )



if __name__ == '__main__':
    unittest.main(verbosity=2)
