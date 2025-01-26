import sys
sys.path.append("../")

import unittest
import sync_model as sm
from prrty_list.prrty_list import PriorityList


class gObject(sm.smRole):
    def __init__(self, log, name, state, priority=0):
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
        self.log( f"interaction: {self.name}" )

    def run_update(self, context=None):
        self.log( f"update: {self.name}" )

    def __str__(self):
        return self.name + ' ' + self.state
    


class TestSyncModel(unittest.TestCase):
    execution_msg_list = []

    def setUp(self):
        self.sm = sm.Sync()    

    @classmethod
    def _log(cls, msg):
        cls.execution_msg_list.append(msg)

    # def test_object(self):
    #     TestSyncModel.execution_msg_list = []
    #     num_Obj = 5
    #     _log = lambda s: TestSyncModel._log(s)
    #     for prio in [9,5,1]:
    #         list = [ gObject( _log, 'obj'+str(prio*100+i), 'state'+str(i),prio) for i in range(num_Obj) ]
    #     list_pl = PriorityList( iter_return_priority=False )
    #     list_pl.add_items(list, lambda obj: obj.get_priority())
        
    #     self.sm.run_single_step(list_pl)

    def test_priority_order(self):
        TestSyncModel.execution_msg_list = []
        num_Obj = 3
        _log = lambda s: TestSyncModel._log(s)
        def go_new(n,s,p):
            return gObject( _log, 'obj'+str(n), 'state'+str(s), p)
        
        list = [ go_new( i,i,i ) for i in range(num_Obj) ]
        list += [ go_new( 10+i,i,i ) for i in range(num_Obj) ]
        list_pl = PriorityList( iter_return_priority=False )
        list_pl.add_items(list, lambda obj: obj.get_priority())
        
        self.sm.run_single_step(list_pl)
        
        expected_order = ['interaction: obj2', 'interaction: obj12',
                          'interaction: obj1', 'interaction: obj11',
                          'interaction: obj0','interaction: obj10',
                          'update: obj2', 'update: obj12',
                          'update: obj1', 'update: obj11',
                          'update: obj0','update: obj10']
        self.assertEqual(TestSyncModel.execution_msg_list, expected_order)

    def test_empty_list(self):
        TestSyncModel.execution_msg_list = []
        list_pl = PriorityList( iter_return_priority=False )
        
        self.sm.run_single_step(list_pl)
        
        self.assertEqual(TestSyncModel.execution_msg_list, [])

    def test_single_object(self):
        TestSyncModel.execution_msg_list = []
        _log = lambda s: TestSyncModel._log(s)
        obj = gObject(_log, 'single_obj', 'state0', priority=1)
        list_pl = PriorityList( iter_return_priority=False )
        list_pl.add_items([obj], lambda obj: obj.get_priority())
        
        self.sm.run_single_step(list_pl)
        
        expected_order = ['interaction: single_obj', 'update: single_obj']
        self.assertEqual(TestSyncModel.execution_msg_list, expected_order)

    def test_same_priority(self):
        TestSyncModel.execution_msg_list = []
        num_Obj = 3
        _log = lambda s: TestSyncModel._log(s)
        list = [ gObject( _log, 'obj'+str(i), 'state'+str(i), priority=1) for i in range(num_Obj) ]
        list_pl = PriorityList( iter_return_priority=False )
        list_pl.add_items(list, lambda obj: obj.get_priority())
        
        self.sm.run_single_step(list_pl)
        
        expected_order = ['interaction: obj0', 'interaction: obj1', 'interaction: obj2',
                            'update: obj0', 'update: obj1', 'update: obj2']
        self.assertEqual(TestSyncModel.execution_msg_list, expected_order)

       


class TestOASCycl(unittest.TestCase):
    execution_msg_list = []

    def setUp(self):
        self.sm = sm.OASCycl()

    @classmethod
    def _log(cls, msg):
        cls.execution_msg_list.append(msg)

    def test_oas_cycl_empty(self):
        TestOASCycl.execution_msg_list = []
        list_pl = PriorityList(iter_return_priority=False)

        self.sm.run_single_step(list_pl)

        self.assertEqual(TestOASCycl.execution_msg_list, [])

    def test_oas_cycl_single_object(self):
        TestOASCycl.execution_msg_list = []
        _log = lambda s: TestOASCycl._log(s)
        obj = gObject(_log, 'oas_single_obj', 'state0', priority=1)
        list_pl = PriorityList(iter_return_priority=False)
        list_pl.add_items([obj], lambda obj: obj.get_priority())

        self.sm.run_single_step(list_pl)

        expected_order = ['interaction: oas_single_obj', 'update: oas_single_obj']
        self.assertEqual(TestOASCycl.execution_msg_list, expected_order)

    def test_oas_cycl_priority_order(self):
        TestOASCycl.execution_msg_list = []
        num_Obj = 3
        _log = lambda s: TestOASCycl._log(s)
        def go_new(n, s, p):
            return gObject(_log, 'oas_obj' + str(n), 'state' + str(s), p)

        list = [go_new(i, i, i) for i in range(num_Obj)]
        list += [go_new(10 + i, i, i) for i in range(num_Obj)]
        list_pl = PriorityList(iter_return_priority=False)
        list_pl.add_items(list, lambda obj: obj.get_priority())

        self.sm.run_single_step(list_pl)

        expected_order = ['interaction: oas_obj2','update: oas_obj2',
                          'interaction: oas_obj12', 'update: oas_obj12',
                            'interaction: oas_obj1', 'update: oas_obj1',
                            'interaction: oas_obj11', 'update: oas_obj11',
                            'interaction: oas_obj0', 'update: oas_obj0',
                            'interaction: oas_obj10', 'update: oas_obj10']
        
        self.assertEqual(TestOASCycl.execution_msg_list, expected_order)

    def test_oas_cycl_same_priority(self):
        TestOASCycl.execution_msg_list = []
        num_Obj = 3
        _log = lambda s: TestOASCycl._log(s)
        list = [gObject(_log, 'oas_obj' + str(i), 'state' + str(i), priority=1) for i in range(num_Obj)]
        list_pl = PriorityList(iter_return_priority=False)
        list_pl.add_items(list, lambda obj: obj.get_priority())

        self.sm.run_single_step(list_pl)
        print(TestOASCycl.execution_msg_list)

        expected_order = [ 'interaction: oas_obj0','update: oas_obj0',
                           'interaction: oas_obj1','update: oas_obj1',
                           'interaction: oas_obj2','update: oas_obj2', 
        ]
        self.assertEqual(TestOASCycl.execution_msg_list, expected_order)


if __name__ == '__main__':
    unittest.main(verbosity=2)