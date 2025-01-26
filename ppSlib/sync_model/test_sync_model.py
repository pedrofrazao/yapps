import unittest
import sync_model as sm


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

    def test_object(self):
        TestSyncModel.execution_msg_list = []
        num_Obj = 5
        list = [ gObject(lambda s: TestSyncModel._log(s),'obj'+str(i), 'state'+str(i)) for i in range(num_Obj) ]
        self.sm.run_single_step(list)

        # print(self.execution_msg_list)
        for i in range(num_Obj):
            self.assertEqual(TestSyncModel.execution_msg_list[i], 'interaction: obj'+str(i))
            self.assertEqual(TestSyncModel.execution_msg_list[num_Obj+i], 'update: obj'+str(i))

        

class TestOASCycl(unittest.TestCase):
    execution_msg_list = []
    @classmethod
    def _log(cls, msg):
        cls.execution_msg_list.append(msg)

    def setUp(self):
        self.sm = sm.OASCycl()

    def test_object(self):
        TestOASCycl.execution_msg_list = []
        num_Obj = 5
        list = [ gObject(lambda s: TestSyncModel._log(s),'obj'+str(i), 'state'+str(i)) for i in range(num_Obj) ]
        self.sm.run_single_step(list)

        # print(TestSyncModel.execution_msg_list)
        for i in range(num_Obj):
            iIndex = i*2
            uIndex = iIndex+1
            self.assertEqual(TestSyncModel.execution_msg_list[iIndex], 'interaction: obj'+str(i))
            self.assertEqual(TestSyncModel.execution_msg_list[uIndex], 'update: obj'+str(i))



if __name__ == '__main__':
    unittest.main(verbosity=2)