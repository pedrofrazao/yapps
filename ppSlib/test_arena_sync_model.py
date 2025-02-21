
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
from ppSlib.arena_sync_model import ArenaSyncModel, asmObject


class TestArenaSyncModel(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='Sync')
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
    def run_interaction(self, context=None):
        if( context is not None and int(context)>0 ):
            s = self.get_obj_state()
            s['e'] += 1
            self.set_obj_state(s)
        return super().run_interaction(context)

class TestArenaSyncModelUpdate(unittest.TestCase):
    def setUp(self):
        self.arena = ArenaSyncModel(5, 5, sync_model='Sync')
        obj1 = agentA("obj1", { 'e': 1, 'f': 0 }, 10)
        obj2 = agentA("obj2", { 'e': 2, 'f': 0 }, 10)
        self.arena.add_to_position(0, 0, obj1)
        self.arena.add_to_position(0, 1, obj2)

    def test_interaction(self):
        self.assertEqual( 1, self.arena.get_position(0, 0)[0].state['e'] )
        self.assertEqual( 2, self.arena.get_position(0, 1)[0].state['e'] )
        o1 = self.arena.get_position(0, 0)[0]
        o2 = self.arena.get_position(0, 1)[0]
        o1.run_interaction( context=0 )
        self.assertEqual( 1, o1.state['e'], "no change on the internal state" )
        self.assertIsNone( o1._next_state, "no next state set" )
        o1.run_interaction( context=1 )
        self.assertEqual( 1, o1.state['e'], "no change on the internal state" )
        self.assertIsNotNone( o1._next_state, "next state set" )
        o2.run_update()
        self.assertEqual( 2, o2.state['e'], "change on the internal state" )
        

if __name__ == '__main__':
    unittest.main( verbosity=4 )