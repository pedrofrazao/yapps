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
        self.arena = Arena(5, 5, 'torus', 2)
        self.obj1 = ArenaObject("Object1")
        self.obj2 = ArenaObject("Object2")
        self.obj3 = ArenaObject("Object3")

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
        self.assertIn(self.obj1, self.arena.get_position(1, 1))
        self.assertEqual( 2, self.arena.num_objects)

    def test_volume_restrictions(self):
        self.arena.add_to_position(1, 1, self.obj1)
        self.arena.add_to_position(1, 1, self.obj2)
        self.assertFalse(self.arena.add_to_position(1, 1, self.obj3))
        self.assertEqual( 2, self.arena.get_num_objects(1, 1))
        self.assertTrue(self.arena.add_to_position(1, 0, self.obj3))
        self.assertFalse( self.arena.move_object_position(1, 0, self.obj3, 'right', 1) )
        self.assertIn(self.obj1, self.arena.get_position(1, 1))
        self.assertIn(self.obj2, self.arena.get_position(1, 1))
        self.assertNotIn(self.obj3, self.arena.get_position(1, 1))
        self.assertIn(self.obj3, self.arena.get_position(1, 0))

    def test_more_moves(self):
        # setup of the arena
        self.assertTrue(self.arena.add_to_position(0, 0, self.obj1))
        self.assertTrue(self.arena.add_to_position(4, 4, self.obj2))
        self.assertTrue(self.arena.add_to_position(0, 4, self.obj3))

        # apply some moves
        self.assertTrue(self.arena.move_object_position(0, 0, self.obj1, 1, 1))
        self.assertIn(self.obj1, self.arena.get_position(4, 4))

        self.assertTrue(self.arena.move_object_position(4, 4, self.obj2, 6, 1))
        self.assertIn(self.obj2, self.arena.get_position(4, 0))

        self.assertTrue(self.arena.move_object_position(0, 4, self.obj3, 3, 1))
        self.assertIn(self.obj3, self.arena.get_position(4, 0))

if __name__ == '__main__':
    unittest.main()