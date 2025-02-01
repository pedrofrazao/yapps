import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest

from ppSlib.arena import Arena, ArenaObject

class TestArena(unittest.TestCase):

    def setUp(self):
        self.arena = Arena(5, 5, 'torus', max_volume_per_position=2)
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

    # def test_set_position(self):
    #     self.arena.set_position(1, 1, [self.obj1, self.obj2])
    #     self.assertEqual(self.arena.get_position(1, 1), [self.obj1, self.obj2])
    #     self.assertEqual( 2, self.arena.get_num_objects(1, 1))

    # def test_del_position(self):
    #     self.arena.set_position(1, 1, [self.obj1, self.obj2])
    #     objects = self.arena.del_position(1, 1)
    #     self.assertEqual(objects, [self.obj1, self.obj2])
    #     self.assertEqual(self.arena.get_position(1, 1), [])

    # def test_move_object_position(self):
    #     self.arena.set_position(1, 1, [self.obj1, self.obj2])
    #     self.arena.move_object_position(self.obj1, 'right', 2)
    #     self.assertNotIn(self.obj1, self.arena.get_position(1, 1))
    #     self.assertIn(self.obj1, self.arena.get_position(1, 3))
    #     self.assertIn(self.obj2, self.arena.get_position(1, 1))
    #     self.arena.move_object_position(self.obj1, 'right', 3)
    #     self.assertIn(self.obj2, self.arena.get_position(1, 1))
    #     self.assertIn(self.obj1, self.arena.get_position(1, 1))
    #     self.assertEqual( 2, self.arena.num_objects)

    def test_volume_restrictions(self):
        self.arena.add_to_position(1, 1, self.obj1)
        self.arena.add_to_position(1, 1, self.obj2)
        self.assertFalse(self.arena.add_to_position(1, 1, self.obj3))
        self.assertEqual( 2, self.arena.get_num_objects(1, 1))
        self.assertTrue(self.arena.add_to_position(1, 0, self.obj3))
        self.assertFalse( self.arena.move_object_position(self.obj3, 'right', 1) )
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
        self.assertTrue(self.arena.move_object_position(self.obj1, 1, 1))
        self.assertIn(self.obj1, self.arena.get_position(4, 4))

        self.assertTrue(self.arena.move_object_position(self.obj2, 6, 1))
        self.assertIn(self.obj2, self.arena.get_position(4, 0))

        self.assertTrue(self.arena.move_object_position(self.obj3, 3, 1))
        self.assertIn(self.obj3, self.arena.get_position(4, 0))




class TestArenaMove(unittest.TestCase):

    def setUp(self):
        self.arena = Arena(5, 5, 'torus', max_volume_per_position=100)
        self.obj1 = ArenaObject("rock",volume=100)
        self.arena.add_to_position(0, 0, self.obj1)
        self.obj2 = ArenaObject("rock",volume=100)
        self.arena.add_to_position(1, 0, self.obj2)
        self.obj3 = ArenaObject("rock",volume=100)
        self.arena.add_to_position(2, 0, self.obj3)

        self.p1 = ArenaObject("p1")
        self.p2 = ArenaObject("p2")
        self.arena.add_to_position(1, 1, self.p1)
        self.arena.add_to_position(1, 1, self.p2)

    def test_moves_volume(self):
        self.assertFalse( self.arena.move_object_position(self.p1, 4, 1) )
        self.assertIn(self.p1, self.arena.get_position(1, 1))
        self.assertFalse( self.arena.move_object_position(self.p1, 7, 1) )
        self.assertIn(self.p1, self.arena.get_position(1, 1))
        self.assertTrue( self.arena.move_object_position(self.p1, 8, 1) )
        self.assertIn(self.p2, self.arena.get_position(1, 1))
        self.assertIn(self.p1, self.arena.get_position(2, 1))
        self.assertTrue( self.arena.move_object_position(self.p1, 7, 1) )
        self.assertIn(self.p2, self.arena.get_position(1, 1))
        self.assertIn(self.p1, self.arena.get_position(3, 0))

class TestArenaSerialize(unittest.TestCase):

    def setUp(self):
        self.arena = Arena(5, 5, 'torus', max_volume_per_position=100)
        self.obj1 = ArenaObject("rock",volume=100)
        self.arena.add_to_position(0, 0, self.obj1)
        self.obj2 = ArenaObject("rock",volume=100)
        self.arena.add_to_position(1, 0, self.obj2)
        self.obj3 = ArenaObject("rock",volume=100)
        self.arena.add_to_position(2, 0, self.obj3)

        self.p1 = ArenaObject("p1")
        self.p2 = ArenaObject("p2")
        self.arena.add_to_position(1, 1, self.p1)
        self.arena.add_to_position(1, 1, self.p2)

    def test_serialize_arena(self):
        serialized_data = self.arena.serialize()
        # print(serialized_data)
        self.assertEqual(serialized_data['rows'], 5)
        self.assertEqual(serialized_data['cols'], 5)
        self.assertEqual(serialized_data['type'], 'torus')
        self.assertEqual(serialized_data['max_volume_per_position'], 100)
        self.assertEqual(serialized_data['num_objects'], 5)

        a2 = Arena.deserialize(serialized_data)
        self.assertEqual(a2.rows, self.arena.rows)
        self.assertEqual(a2.cols, self.arena.cols)
        self.assertEqual(a2.type, self.arena.type)
        self.assertEqual(a2.max_volume_per_position, self.arena.max_volume_per_position)
        self.assertEqual(a2.num_objects, self.arena.num_objects)
        for row in range(self.arena.rows):
            for col in range(self.arena.cols):
                a2_pos_ids = [o.id for o in a2.get_position(row, col)]
                for obj in self.arena.get_position(row, col):
                    self.assertIn(obj.id, a2_pos_ids)



if __name__ == '__main__':
    unittest.main()