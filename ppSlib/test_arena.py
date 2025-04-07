import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest

from ppSlib.arena import Arena, ArenaObject
from ppSlib.arena_surrounding import Surrounding, SurroundingManhattan, SurroundingChebyshev

class TestArena(unittest.TestCase):

    def setUp(self):
        self.arena = Arena(5, 5, arena_type='plan')
        self.obj1 = ArenaObject("Object1",arena=self.arena)
        self.obj2 = ArenaObject("Object2",arena=self.arena)

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

    def test_move_dir_5(self):
        self.arena.add_to_position(1, 1, self.obj1)

        self.arena.move_object_position(self.obj1, 5, 1)
        self.assertIn(self.obj1, self.arena.get_position(1, 1))
        self.assertEqual( 1, self.arena.get_num_objects(1, 1))

        self.arena.move_object_position(self.obj1, 5, 0)
        self.assertIn(self.obj1, self.arena.get_position(1, 1))
        self.assertEqual( 1, self.arena.get_num_objects(1, 1))

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
        self.obj1 = ArenaObject("Object1", arena=self.arena)
        self.obj2 = ArenaObject("Object2", arena=self.arena)
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
        self.obj1 = ArenaObject("Object1", arena=self.arena)
        self.obj2 = ArenaObject("Object2", arena=self.arena)
        self.obj3 = ArenaObject("Object3", arena=self.arena)
        """
        0 0 0 0 0
        0 1 2 0 0
        0 0 0 0 0
        0 0 0 0 3
        """
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

    def test_get_surrounding_objects_with_torus_arena(self):
        self.arena.type = 'torus'
        surrounding = Surrounding(self.arena, 4, 0, length=2)
        self.assertIn(self.obj1, surrounding.objects)
        self.assertIn(self.obj2, surrounding.objects)
        self.assertIn(self.obj3, surrounding.objects)

    def test_distance_manhattan(self):
        obj4 = ArenaObject("Object4", arena=self.arena)
        self.arena.add_to_position(2,2,obj4)
        surrounding = SurroundingManhattan( self.arena, 2, 2, length=1)
        self.assertNotIn(self.obj1, surrounding.objects)
        self.assertIn(self.obj2, surrounding.objects)
        self.assertNotIn(self.obj3, surrounding.objects)

        self.assertEqual(2,surrounding.direction_xy(1,2))
        self.assertIn( (obj4,0,5), surrounding.objects_meta )
        self.assertIn( (self.obj2,1,2), surrounding.objects_meta )

class TestArenaSurrounfingDist(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(5, 5, arena_type='torus')
        self.o1 = ArenaObject("o1", arena=self.arena)
        self.o2 = ArenaObject("o2", arena=self.arena)
        self.o3 = ArenaObject("o3", arena=self.arena)
        self.o4 = ArenaObject("o4", arena=self.arena)
        self.o5 = ArenaObject("o5", arena=self.arena)
        self.o6 = ArenaObject("o6", arena=self.arena)
        """
        56 4 0 0 3
         0 0 0 0 0
         0 0 0 0 0
         0 1 2 0 0
        """
        self.arena.add_to_position(0, 0, self.o5)
        self.arena.add_to_position(0, 0, self.o6)
        self.arena.add_to_position(0, 1, self.o4)
        self.arena.add_to_position(0, 4, self.o3)
        self.arena.add_to_position(4, 1, self.o1)
        self.arena.add_to_position(4, 2, self.o2)

    def test_distance_manhattan(self):
        surrounding = SurroundingManhattan( self.arena, 0, 1, length=1)

        distances = {}
        for obj, distance, direction in surrounding.objects_meta:
            distances[obj.name] = (direction, distance)
        
        self.assertEqual(distances[self.o5.name], (4, 1))
        self.assertEqual(distances[self.o6.name], (4, 1))
        self.assertEqual(distances[self.o4.name], (5, 0))
        self.assertEqual(distances[self.o1.name], (2, 1))
        self.assertEqual(len(distances), 4)

    def test_distance_manhattan2(self):
        surrounding = SurroundingManhattan( self.arena, 0, 0, length=1)

        distances = {}
        for obj, distance, direction in surrounding.objects_meta:
            distances[obj.name] = (direction, distance)
        
        self.assertEqual(distances[self.o5.name], (5, 0))
        self.assertEqual(distances[self.o6.name], (5, 0))
        self.assertEqual(distances[self.o4.name], (6, 1))
        self.assertEqual(distances[self.o3.name], (4, 1))
        self.assertEqual(len(distances), 4)

    def test_distance_manhattan3(self):
        """
        56 4 0 0 3
         0 0 0 0 0
         0 0 0 0 0
         0 1 2 0 0
        """
        surrounding = SurroundingManhattan( self.arena, 0, 0, length=2)

        distances = {}
        for obj, distance, direction in surrounding.objects_meta:
            distances[obj.name] = (direction, distance)
        
        self.assertEqual(distances[self.o5.name], (5, 0))
        self.assertEqual(distances[self.o6.name], (5, 0))
        self.assertEqual(distances[self.o4.name], (6, 1))
        self.assertEqual(distances[self.o3.name], (4, 1))
        dir,dis = distances[self.o1.name]
        self.assertEqual(dis, 2)
        self.assertIn(dir, [2,6])
        self.assertEqual(len(distances), 5)



class TestArenaSurrounfingDist2(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(5, 5, arena_type='torus')
        self.o1 = ArenaObject("o1", arena=self.arena)
        self.o2 = ArenaObject("o2", arena=self.arena)
        self.o3 = ArenaObject("o3", arena=self.arena)
        self.o4 = ArenaObject("o4", arena=self.arena)
        self.o5 = ArenaObject("o5", arena=self.arena)
        self.o6 = ArenaObject("o6", arena=self.arena)
        """
        56 4 0 0 3
         0 0 0 0 0
         0 0 0 0 0
         0 1 2 0 0
        """
        self.arena.add_to_position(0, 0, self.o5)
        self.arena.add_to_position(0, 0, self.o6)
        self.arena.add_to_position(0, 1, self.o4)
        self.arena.add_to_position(0, 4, self.o3)
        self.arena.add_to_position(4, 1, self.o1)
        self.arena.add_to_position(4, 2, self.o2)    

    def test_find_all_position(self):
        surrounding = SurroundingChebyshev( self.arena, 0, 1, length=1)

        pos = surrounding._all_positions_at_distance()
        self.assertEqual(9, len(pos))

        for p in ((4,0), (4,1), (4,2),
                  (0,0), (0,1), (0,2),
                  (1,0), (1,1), (1,2)):
            self.assertIn(p,pos)

        empty = surrounding.find_empty_position()
        self.assertEqual(5, len(empty))
        for p in ((0,2), (1,0), (1,1), (1,2), (4,0)):
            self.assertIn(p,empty)
        for p in ((0,0), (0,1), (4,1), (4,2)):
            self.assertNotIn(p,empty)

    def test_distance_chebyshev(self):
        surrounding = SurroundingChebyshev( self.arena, 0, 1, length=1)

        distances = {}
        for obj, distance, direction in surrounding.objects_meta:
            distances[obj.name] = (direction, distance)
        
        self.assertEqual(distances[self.o5.name], (4, 1))
        self.assertEqual(distances[self.o6.name], (4, 1))
        self.assertEqual(distances[self.o4.name], (5, 0))
        self.assertEqual(distances[self.o1.name], (2, 1))
        self.assertEqual(distances[self.o2.name], (3, 1))
        self.assertEqual(len(distances), 5)

    def test_distance_chebyshev2(self):
        """
        56 4 0 0 3
         0 0 0 0 0
         0 0 0 0 0
         0 1 2 0 0
        """
        surrounding = SurroundingChebyshev( self.arena, 0, 0, length=2)

        distances = {}
        for obj, distance, direction in surrounding.objects_meta:
            distances[obj.name] = (direction, distance)
        
        self.assertEqual(distances[self.o5.name], (5, 0))
        self.assertEqual(distances[self.o6.name], (5, 0))
        self.assertEqual(distances[self.o4.name], (6, 1))
        self.assertEqual(distances[self.o3.name], (4, 1))
        self.assertEqual(distances[self.o1.name], (3, 1))
        self.assertEqual(distances[self.o2.name], (3, 2))

        self.assertEqual(len(distances), 6)

        surrounding = SurroundingChebyshev( self.arena, 0, 0, length=0)
        self.assertIn(self.o5, surrounding.objects)
        self.assertIn(self.o6, surrounding.objects)

class TestArenaSurroundingSort(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(5, 5, arena_type='torus')
        self.o1 = ArenaObject("o1", arena=self.arena)
        self.o2 = ArenaObject("o2", arena=self.arena)
        self.o3 = ArenaObject("o3", arena=self.arena)
        self.o4 = ArenaObject("o4", arena=self.arena)
        self.o5 = ArenaObject("o5", arena=self.arena)
        self.o6 = ArenaObject("o6", arena=self.arena)
        """
         4 0 0 0 3
         0 2 0 0 0
         0 0 1 0 0
         0 0 0 0 0
        """
        self.arena.add_to_position(2, 2, self.o1)
        self.arena.add_to_position(1, 1, self.o2)
        self.arena.add_to_position(0, 0, self.o4)
        self.arena.add_to_position(0, 4, self.o3)


    def test_distance_sort_chebyshev_l1(self):
        surrounding = SurroundingChebyshev( self.arena, 2, 2, length=1)
        so = [ (o,dis,dir) for o,dis,dir in sorted(surrounding, key=lambda x: x[1]) ]
        self.assertEqual(so[0][0], self.o1)
        self.assertEqual(so[1][0], self.o2)

        # dir
        self.assertIn( (self.o1, 0, 5), so)
        self.assertIn( (self.o2, 1, 1), so)
        self.assertEqual(2, len(so), "2 objects")

    def test_distance_sort_chebyshev_l2(self):        
        surrounding = SurroundingChebyshev( self.arena, 2, 2, length=2)
        so = [ (o,dis,dir) for o,dis,dir in sorted(surrounding, key=lambda x: x[1]) ]
        self.assertEqual(so[0][0], self.o1)
        self.assertEqual(so[1][0], self.o2)
        self.assertIn( (self.o4, 2, 1), so)
        self.assertIn( (self.o3, 2, 3), so)

        # dir
        self.assertIn( (self.o1, 0, 5), so)
        self.assertIn( (self.o2, 1, 1), so)
        self.assertIn( (self.o4, 2, 1), so)
        self.assertIn( (self.o3, 2, 3), so)
        self.assertEqual(4, len(so))

    def test_distance_sort_chebyshev_l2s(self):
        so = SurroundingChebyshev( self.arena, 2, 2, length=2).sorted()
        self.assertEqual(so[0][0], self.o1)
        self.assertEqual(so[1][0], self.o2)
        self.assertIn( (self.o4, 2, 1), so)
        self.assertIn( (self.o3, 2, 3), so)

        # dir
        self.assertIn( (self.o1, 0, 5), so)
        self.assertIn( (self.o2, 1, 1), so)
        self.assertIn( (self.o4, 2, 1), so)
        self.assertIn( (self.o3, 2, 3), so)
        self.assertEqual(4, len(so))


class TestArenaSurrounSmall(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(5, 5, arena_type='torus')

    def test_too_large_length(self):
        surrounding = Surrounding(self.arena, 0, 0, length=4)
        empty = surrounding.find_empty_position()
        self.assertEqual(25, len(empty))
        c=0
        for x,y in empty:
            o1 = ArenaObject( arena=self.arena)
            self.arena.add_to_position(x,y,o1)
            c += 1
            e = Surrounding(self.arena, 0, 0, length=4).find_empty_position()
            self.assertEqual(25-c, len(e))
            
        e = Surrounding(self.arena, 0, 0, length=4).find_empty_position()
        self.assertEqual(0, len(e))

if __name__ == '__main__':
    unittest.main(verbosity=2)