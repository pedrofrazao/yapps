import unittest
import sys
import os

# Adjust the path to include the parent directory of the 'arena' package
dirname = os.path.dirname(__file__)
libpath = os.path.abspath(os.path.join(dirname, '..', 'ppSlib'))
sys.path.append(libpath)

from arena import Arena, ArenaObject

class TestArena(unittest.TestCase):

    def setUp(self):
        self.arena = Arena(5, 5)
        self.obj1 = ArenaObject("Object1")
        self.obj2 = ArenaObject("Object2")

    def test_add_to_position(self):
        self.arena.add_to_position(1, 1, self.obj1)
        self.assertIn(self.obj1, self.arena.get_position(1, 1))

    def test_add_a_2nd_object_to_position(self):
        self.assertEqual( 0, self.arena.get_num_objects(1, 1))
        self.arena.add_to_position(1, 1, self.obj1)
        self.assertEqual( 1, self.arena.get_num_objects(1, 1))
        self.arena.add_to_position(1, 1, self.obj2)
        self.assertIn(self.obj1, self.arena.get_position(1, 1))
        self.assertIn(self.obj2, self.arena.get_position(1, 1))
        self.assertEqual( 2, self.arena.get_num_objects(1, 1))

    def test_remove_from_position(self):
        self.arena.add_to_position(1, 1, self.obj1)
        self.arena.remove_from_position(1, 1, self.obj1)
        self.assertNotIn(self.obj1, self.arena.get_position(1, 1))
        self.assertEqual( 0, self.arena.get_num_objects(1, 1))

    def test_set_position(self):
        self.arena.set_position(1, 1, [self.obj1, self.obj2])
        self.assertEqual(self.arena.get_position(1, 1), [self.obj1, self.obj2])
        self.assertEqual( 2, self.arena.get_num_objects(1, 1))

    def test_del_position(self):
        self.arena.set_position(1, 1, [self.obj1, self.obj2])
        objects = self.arena.del_position(1, 1)
        self.assertEqual(objects, [self.obj1, self.obj2])
        self.assertEqual(self.arena.get_position(1, 1), [])

    def test_move_object_position(self):
        self.arena.set_position(1, 1, [self.obj1, self.obj2])
        self.arena.move_object_position(1, 1, self.obj1, 'right', 2)
        self.assertNotIn(self.obj1, self.arena.get_position(1, 1))
        self.assertIn(self.obj1, self.arena.get_position(1, 3))
        self.assertIn(self.obj2, self.arena.get_position(1, 1))
        self.arena.move_object_position(1, 3, self.obj1, 'right', 3)
        self.assertIn(self.obj2, self.arena.get_position(1, 1))
        self.assertNotIn(self.obj1, self.arena.get_position(1, 1))
        self.assertEqual( 1, self.arena.num_objects)

if __name__ == '__main__':
    unittest.main()