"""
connection between arena and sync_model
"""
from ppSlib.arena import Arena, ArenaObject
from ppSlib.sync_model.sync_model_prrt_list import SyncModelPrrtList
from ppSlib.sync_model.sync_model import smRole

class ArenaSyncModel(Arena):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stype = kwargs.get('sync_model', 'Sync')
        self.sync_model = SyncModelPrrtList(sync_model=stype)

    def add_to_position(self, x, y, obj):
        super().add_to_position(x, y, obj)
        self.sync_model.add_item(obj, obj.get_priority())

    def remove_from_position(self, x, y, obj):
        super().remove_from_position(x, y, obj)
        self.sync_model.remove_item(obj, priority=obj.get_priority())


class asmObject(ArenaObject,smRole):
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
        return self.name