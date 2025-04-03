
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from pprint import pprint
import unittest
from ppSlib.arena_sync_model import ArenaSyncModel, asmObject, asmState
from ppSlib.agent import Agent, Carnivore, Prey, Block, Trap, LivingAgent


class TestArenaSyncModel(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5)
        obj1 = asmObject("obj1", {}, 10)
        obj2 = asmObject("obj2", {}, 10)
        self.arena.add_to_position(0, 0, obj1)
        self.arena.add_to_position(0, 1, obj2)
        self.__print_arena()

    def __print_arena(self):
        # print( f"\n{self.arena}" )
        pass

    def test_arena_object_count(self):
        self.assertEqual( 2, len(self.arena.sync_model.priority_dict.get(10)) )
        self.assertEqual( 2, self.arena.num_objects)
        # print( self.arena.sync_model.priority_dict.get(10) )
        ## remove 1 object
        o = self.arena.get_position(0, 0)[0]
        self.assertIsInstance(o, asmObject)
        self.arena.remove_from_position(0, 0, o)
        ## check object count
        self.assertEqual( 1, len(self.arena.sync_model.priority_dict.get(10)) )
        self.assertEqual( 1, self.arena.num_objects)
        self.__print_arena()


class agentA(asmObject):
    def see(self,state):
        return None
    
    # def run_interaction(self, context=None):
    #     if( context is not None and int(context)>0 ):
    #         self.add2sattr('e', 1)
    #     return super().run_interaction(context)
    

class agentB(Agent):
    def __init__(self, state_args, arena):
        state_args['epoch_penalty'] = 1
        super().__init__(state_args=state_args, arena=arena)

    def select_action(self,state,surroundings):
        self.setsattr('direction',6)
        return "move", { 'direction': 6 }

    def do_action(self,action,action_args):
        if( action == "move" ):
            return self.move(action_args['direction'], 1)
        return False

class TestArenaSyncModelUpdate(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5)
        obj1 = agentA("obj1", { 'e': 1, 'f': 0 }, 10)
        obj2 = agentA("obj2", { 'e': 2, 'f': 0 }, 10)
        self.arena.add_to_position(0, 0, obj1)
        self.arena.add_to_position(0, 1, obj2)

    def test_interaction(self):
        # 'e' values before interaction
        self.assertEqual( 1, self.arena.get_position(0, 0)[0].getsattr('e') )
        self.assertEqual( 2, self.arena.get_position(0, 1)[0].getsattr('e') )
        o1 = self.arena.get_position(0, 0)[0]
        o2 = self.arena.get_position(0, 1)[0]
        # interaction
        o1.run_interaction( context=0 )
        # 'e' values after interaction but before update
        self.assertEqual( 1, o1.getsattr('e'), "no change on the internal state" )
        self.assertIsNone( o1.asmstate._next_state, "no next state set" )

        o1.run_interaction( context=1 )
        self.assertEqual( 1, o1.getsattr('e'), "no change on the internal state" )
        self.assertIsNotNone( o1.asmstate.get_next_state(), "next state set" )

        # update and check the 'e' values
        o2.run_update()
        self.assertEqual( 2, o2.getsattr('e'), "change on the internal state" )


class TestArenaRun(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5)
        obj1 = agentB( state_args={ 'energy':10, 'direction':5}, arena=self.arena)
        self.arena.add_to_random_position(obj1)

    def test_run(self):
        self.assertEqual( 1, self.arena.num_objects )
        o = self.arena.get_objects()[0]
        y = o.y  # store y position
        # print( f"o: {o.nickname}: {o.x},{o.y} - {o.direction()}" )
        self.arena.run_step()
        # print("after run_step")
        self.assertEqual( 6, o.direction() )
        # print( f"o: {o.nickname}: {o.x},{o.y} - {o.direction()}" )
        self.assertNotEqual( y, o.y, "move dir 6" )
        self.assertEqual( 1, self.arena.num_objects )

    def test_run_many(self):
        self.assertEqual( 1, self.arena.num_objects )
        o = self.arena.get_objects()[0]
        x,y = o.x, o.y
        for i in range(5):
            self.arena.run_step()
            # print( f">> { o.get_state() }" )
            try:
                self.assertEqual( 6, o.direction() )
                self.assertNotEqual( (x,y), (o.x, o.y), "move" )
                x,y = o.x, o.y
            except AssertionError as e:
                # print(f"Assertion failed: {e}")
                # print( f">> { o.get_state() }" )
                raise AssertionError(f"Assertion failed: {e}. Internal state of 'o': {o.get_state()}")
            self.assertEqual( 1, self.arena.num_objects )

if __name__ == '__main__':
    unittest.main( verbosity=4 )