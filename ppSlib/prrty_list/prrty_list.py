import random

class PriorityObject:
    def __init__(self, item, priority):
        self.item = item
        self.priority = priority

class PriorityList:
    def __init__(self):
        self.priority_dict = {}
        self._current_priority = None
        self._current_index = 0

    def add_items(self, items, call2priority):
        for item, priority in items:
            self.add_item(item, call2priority(item))

    def add_item(self, item, priority):
        if priority not in self.priority_dict:
            self.priority_dict[priority] = []
        self.priority_dict[priority].append(PriorityObject(item, priority))

    def remove_item_from_priority(self, item, priority):
        if priority in self.priority_dict:
            for obj in self.priority_dict[priority]:
                if obj.item == item:
                    return self.priority_dict[priority].remove(obj)

    def remove_item(self, item, priority=None):
        if priority is not None:
            return self.remove_item_from_priority(item, priority)
        else:
            for priority in self.priority_dict:
                r = self.remove_item(item, priority)
                if r:
                    return r

    def get_items(self):
        items = []
        for priority in sorted(self.priority_dict.keys()):
            items.extend((obj.item, obj.priority) for obj in self.priority_dict[priority])
        return items

    def __iter__(self):
        self._current_priority_iter = iter(sorted(self.priority_dict.keys()))
        self._current_index = 0
        self._current_list = None
        return self

    def __next__(self):
        if self._current_list is None or self._current_index >= len(self._current_list):
            self._current_priority = next(self._current_priority_iter)
            self._current_list = self.priority_dict[self._current_priority]
            self._current_index = 0

        if self._current_index < len(self._current_list):
            item = self._current_list[self._current_index]
            self._current_index += 1
            return item.item, item.priority
        else:
            raise StopIteration

class ShuffledPriorityList(PriorityList):
    def __init__(self):
        super().__init__()
        self._shuffled = False

    def shuffle_within_priority(self):
        for priority in self.priority_dict:
            random.shuffle(self.priority_dict[priority])