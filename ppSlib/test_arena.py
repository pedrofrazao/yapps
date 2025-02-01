import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest

from ppSlib.arena import Arena, ArenaObject, Surrounding

class TestArena(unittest.TestCase):

    def setUp(self):
        self.arena = Arena(5, 5, arena_type='plan')
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
    #     self.assertNotIn(self.obj1, self.arena.get_position(1, 1))
    #     self.assertEqual( 1, self.arena.num_objects)

class TestArenaSerialization(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(5, 5, arena_type='plan')
        self.obj1 = ArenaObject("Object1")
        self.obj2 = ArenaObject("Object2")
        self.arena.add_to_position(1, 1, self.obj1)
        self.arena.add_to_position(2, 2, self.obj2)

    def test_serialize_arena(self):
        serialized_data = self.arena.serialize()
        self.assertEqual(serialized_data['rows'], 5)
        self.assertEqual(serialized_data['cols'], 5)
        self.assertEqual(serialized_data['type'], 'plan')
        self.assertEqual(serialized_data['max_volume_per_position'], 100)
        self.assertEqual(serialized_data['num_objects'], 2)

        deserialized_arena = Arena.deserialize(serialized_data)
        self.assertEqual(deserialized_arena.rows, 5)
        self.assertEqual(deserialized_arena.cols, 5)
        self.assertEqual(deserialized_arena.type, 'plan')
        self.assertEqual(deserialized_arena.max_volume_per_position, 100)
        self.assertEqual(deserialized_arena.num_objects, 2)
        self.assertEqual(len(deserialized_arena.get_position(1, 1)), 1)
        self.assertEqual(len(deserialized_arena.get_position(2, 2)), 1)
        self.assertEqual(deserialized_arena.get_position(1, 1)[0].name, "Object1")
        self.assertEqual(deserialized_arena.get_position(2, 2)[0].name, "Object2")

class TestArenaSurrounding(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(5, 5, arena_type='plan')
        self.obj1 = ArenaObject("Object1")
        self.obj2 = ArenaObject("Object2")
        self.obj3 = ArenaObject("Object3")
        self.arena.add_to_position(1, 1, self.obj1)
        self.arena.add_to_position(1, 2, self.obj2)
        self.arena.add_to_position(4, 4, self.obj3)

    def test_get_surrounding_objects(self):
        surrounding = Surrounding(self.arena, 2, 2, length=1)
        self.assertIn(self.obj1, surrounding.objects)
        self.assertIn(self.obj2, surrounding.objects)
        self.assertNotIn(self.obj3, surrounding.objects)

    def test_get_surrounding_objects_with_different_length(self):
        surrounding = Surrounding(self.arena, 2, 2, length=2)
        self.assertIn(self.obj1, surrounding.objects)
        self.assertIn(self.obj2, surrounding.objects)
        self.assertIn(self.obj3, surrounding.objects)

    def test_get_surrounding_objects_with_no_objects(self):
        surrounding = Surrounding(self.arena, 4, 0, length=1)
        self.assertEqual(len(surrounding.objects), 0)

    def test_get_surrounding_objects_with_edge_position(self):
        surrounding = Surrounding(self.arena, 4, 0, length=1)
        self.assertEqual(len(surrounding.objects), 0)

    def test_get_surrounding_objects_with_torus_arena(self):
        self.arena.type = 'torus'
        surrounding = Surrounding(self.arena, 4, 0, length=1)
        self.assertNotIn(self.obj1, surrounding.objects)
        self.assertNotIn(self.obj2, surrounding.objects)
        self.assertIn(self.obj3, surrounding.objects)


if __name__ == '__main__':
    unittest.main()