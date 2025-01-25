import random

class PriorityObject:
    def __init__(self, item, priority):
        self.item = item
        self.priority = priority

class PriorityList:
    def __init__(self):
        self.priority_dict = {}

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

    def shuffle_within_priority(self):
        for priority in self.priority_dict:
            random.shuffle(self.priority_dict[priority])

    def get_items(self):
        items = []
        for priority in sorted(self.priority_dict.keys()):
            items.extend((obj.item, obj.priority) for obj in self.priority_dict[priority])
        return items

    def __iter__(self):
        for item, priority in self.get_items():
            yield item, priority

class ShuffledPriorityList(PriorityList):
    def __init__(self):
        super().__init__()
        self._shuffled = False

    def __iter__(self):
        if not self._shuffled:
            self.shuffle_within_priority()
            self._shuffled = True
        for item, priority in self.get_items():
            yield item, priority