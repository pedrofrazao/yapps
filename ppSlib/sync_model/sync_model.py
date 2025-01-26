from abc import ABC, abstractmethod


class smRole:
    @abstractmethod
    def get_obj_state(self):
        raise NotImplementedError("Subclasses must override get_obj_state()")
    @abstractmethod
    def set_obj_state(self, state):
        raise NotImplementedError("Subclasses must override set_obj_state()")
    @abstractmethod
    def run_interaction(self, context=None):
        raise NotImplementedError("Subclasses must override run_interaction()")
    @abstractmethod
    def run_update(self, context=None):
        raise NotImplementedError("Subclasses must override run_update()")
    @abstractmethod
    def __lt__(self, other):
        ## sort by priority, higher priority first
        return self.get_priority() > other.get_priority()

class SyncModel:
    # def run_single_step(self, obj_list):
    #     pass
    # def run_interaction(self, context=None):
    #     raise NotImplementedError("Subclasses must override run_interaction()")
    # def run_update(self, obj_list):
    #     pass
    # def _sort_list(self, obj_list):
    #     pass

    @abstractmethod
    def run_step(self, obj_list):
        pass

    @abstractmethod
    def run_obj_step(self, obj):
        pass

    @abstractmethod
    def run_obj_interaction(self, obj):
        pass

    @abstractmethod
    def run_obj_update(self, obj):
        pass

    # need to be overridden at the mixin level
    @abstractmethod
    def set_obj_state(self, obj, state):
        pass

    # need to be overridden at the mixin level
    @abstractmethod
    def get_obj_state(self, obj):
        pass
    
    def __str__(self):
        return "update schema: "+self.__class__.__name__

class Sync(SyncModel):
    def _sort_list(self, obj_list):
        return sorted(obj_list)
    def run_single_step(self, obj_list):
        for obj in obj_list:
            obj.run_interaction()

        for obj in obj_list:
            obj.run_update()


class OASCycl(SyncModel):
    # def _sort_list(self, obj_list):
    #     return sorted(obj_list)
    def run_single_step(self, obj_list):
        for obj in obj_list:
            obj.run_interaction()
            obj.run_update()


class tObj(SyncModel):
    def __init__(self,prio,state):
        self.prio = prio
        self.state = state

    def run_interaction(self):
        print(f"running interaction {self.state['v']}")

    def run_update(self):
        print(f"running update {self.state['v']}")
    
    def __lt__(self, other):
        return self.prio < other.prio


def main():
    obj1 = tObj(prio=1, state={"v":1})
    obj2 = tObj(prio=10, state={"v":2})
    obj3 = tObj(prio=10, state={"v":3})
    obj4 = tObj(prio=1, state={"v":4})
    obj5 = tObj(prio=1, state={"v":5})
    sync = Sync()
    sync.run_single_step([obj1, obj2, obj3, obj4, obj5])

    sync = OASCycl()
    sync.run_single_step([obj1, obj2, obj3, obj4, obj5])

if __name__ == "__main__":
    main()