"""
This package connect the synchronization model with the priority list.
"""
import ppSlib.sync_model.sync_model as sm
import ppSlib.prrty_list.prrty_list as pl

class SyncModelPrrtList(pl.PriorityList):
    def __init__(self, sync_model='OASCycl'):
        super().__init__(iter_return_priority=False)
        self.sync_model = sm.sync_model_factory(sync_model)

    def run_step(self):
        self.run_single_step(self)
        
    def run_single_step(self):
        self.sync_model.run_single_step(self)

if __name__ == '__main__':
    print(SyncModelPrrtList())