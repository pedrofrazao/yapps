import random

class PriorityObject:
    def __init__(self, item, priority):
        self.item = item
        self.priority = priority

class PriorityList:
    def __init__(self, **kwargs):
        """
        Initializes the priority list with optional keyword arguments.

        Parameters:
        kwargs (dict): Optional keyword arguments.
            - iter_return_priority (bool): If True, the iterator will return priorities. Default is True.
        """
        self.priority_dict = {}
        self._current_priority = None
        self._current_index = 0
        self._iter_return_priority = kwargs.get('iter_return_priority', True)
        self._iter_list = []
        self._iter_removed = []


    def add_items(self, items, call2priority):
        if not callable(call2priority):
            raise ValueError("call2priority must be a callable function")
        for item in items:
            self.add_item(item, call2priority(item))

    def add_item(self, item, priority):
        if priority not in self.priority_dict:
            self.priority_dict[priority] = []
        self.priority_dict[priority].append(PriorityObject(item, priority))

    def remove_item_from_priority(self, item, priority):
        if priority in self.priority_dict:
            for obj in self.priority_dict[priority]:
                if obj.item == item:
                    self.marked_as_removed( obj )
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

    def marked_as_removed(self, obj):
        if self._iter_list:
            self._iter_removed.append(obj.item)

    def __iter__(self):
        self._iter_list = []
        self._iter_removed = []
        ## create a list with all the ordered items, to help on the iteration
        for plist in sorted(self.priority_dict.keys(), reverse=True):
            self._iter_list.extend( [ item for item in self.priority_dict[plist] ] )

        return self        

    def __next__(self):
        v = self._next()
        if v is not None:
            return (v.item, v.priority) if self._iter_return_priority else v.item
        else:
            raise StopIteration

    def _next(self):
        if( not self._iter_list ):
            ## empty iter list
            ## clean up
            self._iter_list = []
            self._iter_removed = []
            return None

        item = self._iter_list.pop(0)
        
        if item.item not in self._iter_removed:
            ## check if item is in the current priority list
            return item
        else:
            ## item was removed, try next
            return self._next()

class ShuffledPriorityList(PriorityList):
    def __init__(self):
        super().__init__()
        self._shuffled = False

    def shuffle_within_priority(self):
        for priority in self.priority_dict:
            random.shuffle(self.priority_dict[priority])