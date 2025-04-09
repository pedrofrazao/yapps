"""
connection between arena and sync_model
"""
from ppSlib.arena import Arena, ArenaObject
from ppSlib.sync_model.sync_model_prrt_list import SyncModelPrrtList
from ppSlib.sync_model.sync_model import smRole
from ppSlib.asmStats import asmStats
# import weakref

class ArenaSyncModel(Arena,asmStats):
    """
    class to connect the arena with the sync_model
    - add_to_position() / remove_from_position()
    - run_step()
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stype = kwargs.get('sync_model', 'OASCycl')
        self.sync_model = SyncModelPrrtList(sync_model=stype)
        self.epoch = 0
        asmStats.__init__(self,**kwargs)

    def add_to_position(self, x, y, obj):
        t = super().add_to_position(x, y, obj)
        if(t):
            self.sync_model.add_item(obj, obj.get_priority())
            return t
        else:
            return False

    def remove_from_position(self, x, y, obj):
        remove = super().remove_from_position(x, y, obj)
        if(remove is not None):
            self.sync_model.remove_item(obj, priority=obj.get_priority())

    def run_step(self):
        self.sync_model.run_single_step()
        self.epoch += 1
        # to collect some stats about the arena
        asmStats.run_step(self)

    def __str__(self):
        arena_str = str(self.epoch) + super().__str__()
        return arena_str

class asmState():
    def __init__(self, state, asmobject=None):
        self.state = state
        self._next_state = None
        self._tmp = {}
        # self.asmobject = weakref.ref(asmobject) if asmobject is not None else None


    def get_asmobject(self):
        if self.asmobject is not None:
            return self.asmobject()
        return None
    
    def clone_state(self):
        return self.state.copy()

    def get_curr_state(self):
        return self.state

    def get_next_state(self):
        if self._next_state is None:
            self._next_state = self.state.copy()
        return self._next_state

    def setsattr(self, attr, value):
        self.state[attr] = value

    def getsattr(self, attr, default=None):
        return self.state.get(attr, default)

    def t_set_attr(self, attr, value):
        """temporary set attribute"""
        ns = self.get_next_state()
        if attr in ns:
            ns[attr] = value
        else:
            self._tmp[attr] = value
        return
    
    def t_get_attr(self, attr, default=None):
        """temporary get attribute"""
        v = self._tmp.get(attr, None)
        if v is None:
            ns = self.get_next_state()
            v = ns.get(attr, None)
        if v is None:
            v = self.getsattr(attr, default)
        return v

    def saw(self):
        """get the surrounding of the object"""
        s = self.t_get_attr('surroundings', None)
        if s is None:
            return None
        return s

    # def saw(self, species=False):
    #     """get the surrounding of the object
    #     species: if True, return only elements of a certain species
    #     """
    #     s = self.t_get_state('surroundings', None)
    #     if s is None:
    #         return None
        
    #     if species:
    #         return map( lambda x: x.species(), s.objects)
    #     else:
    #         return s

    def switch_to_next_state(self):
        if self._next_state is not None:
            self.state = self._next_state
            self._next_state = None
        self._tmp = {}
        return

    def __setitem__(self, key, value):
        """Support item assignment"""
        self.setsattr(key, value)

    def __getitem__(self, key):
        """Support item retrieval"""
        return self.getsattr(key)

    def __str__(self):
        return str(self.state)
    
    def __dump__(self):
        return f"current state: {str(self.state)}\nnext state: {str(self._next_state)}\ntmp data: {str(self._tmp)}"

class asmObject(ArenaObject,smRole):
    """
    class to connect the arena object with the sync_model object
    - get_obj_state() / set_obj_state()
    - get_priority()
    - run_interaction() / run_update()
    """
    def __init__(self, name, state, priority=0, log=None, **kwargs):
        super().__init__(name, **kwargs)
        self.asmstate = asmState(state,asmobject=self)
        self.priority = priority
        self.log = log if log is not None else self.add_msg

    def state(self):
        return self.asmstate.state

    def get_obj_state(self):
        return self.asmstate.state.copy()
    
    def get_next_obj_state(self):
        return self.asmstate._next_state

    def set_obj_state(self, state = None):
        if state is None:
            self.state.switch_to_next_state()
        else:
            self.state = state

    def get_priority(self):
        return self.priority

    def getsattr(self, attr, default=None):
        # s = self.asmstate.get_curr_state()
        return self.asmstate.getsattr(attr, default)
    
    def setsattr(self, attr, value):
        ns = self.asmstate.get_next_state()
        ns[attr] = value

    def add2sattr(self, attr, value):
        ns = self.asmstate.get_next_state()
        ns[attr] = ns.get(attr,0) + value

    def run_interaction(self, context=None):
        self.empty_msg()
    #     if(self.log):
    #         self.log( f"interaction: {self.name}" )

    def run_update(self, context=None):
        # if(self.log):
        #     self.log( f"update: {self.name}" )
        self.asmstate.switch_to_next_state()

    def move(self,direction, distance):
        """Move the object in the arena"""     
        self.arena.move_object_position(self, direction, distance)
        return

    def add_object(self, obj, x, y):
        """Add an object to the arena"""
        self.arena.add_to_position(x, y, obj)
        return

    def __str__(self):
        return self.name + " " + str(self.state)
    
    def extra_info(self):
        return self.asmstate.__dump__()