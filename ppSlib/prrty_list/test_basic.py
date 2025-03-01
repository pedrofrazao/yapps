import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ppSlib.prrty_list.prrty_list import PriorityList, ShuffledPriorityList

class TestPriorityList(unittest.TestCase):
    def setUp(self):
        self.priority_list = PriorityList()

    def test_add_item(self):
        self.priority_list.add_item('item1', 1)
        self.assertIn('item1', [ i.item for i in self.priority_list.priority_dict[1]] )

    def test_remove_item(self):
        self.priority_list.add_item('item1', 1)
        self.priority_list.remove_item('item1')
        self.assertNotIn('item1', [ i.item for i in self.priority_list.priority_dict[1]] )

    def test_shuffle_within_priority(self):
        self.priority_list.add_item('item1', 1)
        self.priority_list.add_item('item2', 1)
        #self.priority_list.shuffle_within_priority()
        self.assertEqual(len(self.priority_list.priority_dict[1]), 2)
        self.assertIn('item1', [ i.item for i in self.priority_list.priority_dict[1]] )
        self.assertIn('item2', [ i.item for i in self.priority_list.priority_dict[1]] )

    def test_get_items(self):
        self.priority_list.add_item('item1', 1)
        self.priority_list.add_item('item2', 2)
        items = self.priority_list.get_items()
        self.assertEqual(items, [('item1', 1), ('item2', 2)])

    def test_iter(self):
        self.priority_list.add_item('item1', 11)
        self.priority_list.add_item('item2', 22)
        self.priority_list.add_item('item3', 11)
        self.priority_list.add_item('item4', 11)
        iter_list_result = [ item for item in self.priority_list ]
        self.assertEqual(iter_list_result, [('item2', 22), ('item1', 11),('item3', 11),('item4', 11) ])


class TestPriorityListCornerCases(unittest.TestCase):
    def setUp(self):
        self.priority_list = PriorityList()
        
    def test_1element_iter(self):
        self.priority_list.add_item('item1', 11)
        iter_list_result = [ item for item in self.priority_list ]
        self.assertEqual(iter_list_result, [('item1', 11) ])

    def test_2element_iter(self):
        self.priority_list.add_item('item1', 11)
        self.priority_list.add_item('item2', 21)
        iter_list_result = [ item for item in self.priority_list ]
        self.assertEqual(iter_list_result, [('item2', 21), ('item1', 11) ])

    def test_3element_iter(self):
        self.priority_list.add_item('item0', 1)
        self.priority_list.add_item('item1', 11)
        self.priority_list.add_item('item2', 21)
        self.priority_list.add_item('item3', 21)

        self.assertEqual( len(self.priority_list.priority_dict[1]), 1)
        self.assertEqual( len(self.priority_list.priority_dict[11]), 1)
        self.assertEqual( len(self.priority_list.priority_dict[21]), 2)

        l = iter(self.priority_list)
        v = next(l)
        self.assertEqual(v, ('item2', 21) )
        self.priority_list.remove_item('item3')
        self.priority_list.remove_item('item1')
        self.priority_list.add_item('item4', 0)
        v = next(l)
        self.assertEqual(v, ('item0', 1) )
        self.assertRaises(StopIteration, next, l)


class TestShuffledPriorityList(unittest.TestCase):
    def setUp(self):
        self.shuffled_priority_list = ShuffledPriorityList()

    def test_add_item(self):
        self.shuffled_priority_list.add_item('item1', 1)
        self.assertIn('item1', [ i.item for i in self.shuffled_priority_list.priority_dict[1]] )

    def test_remove_item(self):
        self.shuffled_priority_list.add_item('item1', 1)
        self.shuffled_priority_list.remove_item('item1')
        self.assertNotIn('item1', [ i.item for i in self.shuffled_priority_list.priority_dict[1]] )

if __name__ == '__main__':
    unittest.main()