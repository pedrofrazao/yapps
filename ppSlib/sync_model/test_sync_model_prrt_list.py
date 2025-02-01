import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from ppSlib.sync_model.sync_model_prrt_list import SyncModelPrrtList
import ppSlib.sync_model.sync_model as sm

class gObject(sm.smRole):
    """
    Simple class only for testing purposes
    Attributes:
    - name: object name
    - state: object with internal state
    - priority: object priority
    - log: DEBUG function to log messages
    """
    def __init__(self, name, state, priority=0, log=None):
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
        return self.name + ' ' + self.state + ' ' + str(self.priority)



class TestSyncModelPrrtList(unittest.TestCase):
    def setUp(self):
        self.sync_model_prrt_list = SyncModelPrrtList()
        smpl = self.sync_model_prrt_list
        for i,p in ((1,11),(2,22),(3,11),(4,11),(5,22),(6,1)):
            o = gObject('item'+str(i), 'state'+str(i), priority=p)
            smpl.add_item(o, o.get_priority())

    def test_initialization_prrt_list(self):
        self.assertIsNotNone(self.sync_model_prrt_list.sync_model)

        iter_list_result = [ item for item in self.sync_model_prrt_list ]
        name_list = [ i.name for i in iter_list_result ]
        self.assertEqual(name_list, ['item2', 'item5', 'item1','item3','item4','item6' ])


class TestSyncModelPart(unittest.TestCase):
    execution_msg_list = []

    def setUp(self):
        self.sync_model_prrt_list = SyncModelPrrtList()
        smpl = self.sync_model_prrt_list
        for i,p in ((1,11),(2,22),(3,11),(4,11),(5,22),(6,1)):
            o = gObject('item'+str(i), 'state'+str(i), priority=p, log=lambda s: TestSyncModelPart._log(s))
            smpl.add_item(o, o.get_priority())

    @classmethod
    def _log(cls, msg):
        """only to identify the order of execution"""
        cls.execution_msg_list.append(msg)

    def test_sync_model(self):
        # clean exec list
        TestSyncModelPart.execution_msg_list = []

        self.sync_model_prrt_list.run_single_step()

        # print(TestSyncModelPart.execution_msg_list)
        self.assertEqual(TestSyncModelPart.execution_msg_list,
                         ['interaction: item2', 'update: item2',
                            'interaction: item5', 'update: item5',
                            'interaction: item1', 'update: item1',
                            'interaction: item3', 'update: item3',
                            'interaction: item4', 'update: item4',
                            'interaction: item6', 'update: item6' ])

if __name__ == '__main__':
    unittest.main()
