"""
connection between arena and sync_model
"""
from ppSlib.arena import Arena, ArenaObject
from ppSlib.sync_model.sync_model_prrt_list import SyncModelPrrtList
from ppSlib.sync_model.sync_model import smRole

class ArenaSyncModel(Arena):
    """
    class to connect the arena with the sync_model
    - add_to_position() / remove_from_position()
    - run_step()
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stype = kwargs.get('sync_model', 'Sync')
        self.sync_model = SyncModelPrrtList(sync_model=stype)
        self.epoch = 0

    def add_to_position(self, x, y, obj):
        super().add_to_position(x, y, obj)
        self.sync_model.add_item(obj, obj.get_priority())

    def remove_from_position(self, x, y, obj):
        super().remove_from_position(x, y, obj)
        self.sync_model.remove_item(obj, priority=obj.get_priority())

    def run_step(self):
        self.sync_model.run_single_step()
        self.epoch += 1

    def __str__(self):
        arena_str = str(self.epoch) + super().__str__()
        return arena_str

class asmObject(ArenaObject,smRole):
    """
    class to connect the arena object with the sync_model object
    - get_obj_state() / set_obj_state()
    - get_priority()
    - run_interaction() / run_update()
    """
    def __init__(self, name, state, priority=0, log=None):
        super().__init__(name, volume=1)
        self.name = name
        self.state = state
        self.priority = priority
        self.log = log

    def get_obj_state(self):
        return self.state

    def set_obj_state(self, state):
        self.state = state

    def get_priority(self):
        return self.priority

    def run_interaction(self, context=None):
        if(self.log):
            self.log( f"interaction: {self.name}" )

    def run_update(self, context=None):
        if(self.log):
            self.log( f"update: {self.name}" )

    def __str__(self):
        return self.name + " " + str(self.state)