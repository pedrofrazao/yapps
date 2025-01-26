import unittest
from prrty_list import PriorityList, ShuffledPriorityList

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
        self.priority_list.add_item('item1', 1)
        self.priority_list.add_item('item2', 2)
        items = list(self.priority_list)
        self.assertEqual(items, [('item1', 1), ('item2', 2)])

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