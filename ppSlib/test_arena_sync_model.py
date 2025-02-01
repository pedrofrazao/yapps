
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

if __name__ == '__main__':
    unittest.main( verbosity=2 )