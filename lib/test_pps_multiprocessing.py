import unittest
import multiprocessing
import os
from pps_multiprocessing import SharedMemoryManager

class TestSharedMemoryManager(unittest.TestCase):
    def setUp(self):
        self.shared_memory = SharedMemoryManager()

    def test_set_and_get_value(self):
        print(f"Process ID: {os.getpid()} - Running test_set_and_get_value")
        self.shared_memory.set_value("key1", 100)
        self.assertEqual(self.shared_memory.get_value("key1"), 100)

    def test_add_value(self):
        print(f"Process ID: {os.getpid()} - Running test_add_value")
        self.shared_memory.set_value("key2", 10)
        self.shared_memory.add_value("key2", 5)
        self.assertEqual(self.shared_memory.get_value("key2"), 15)

    def test_push_to_list_and_pop_from_list(self):
        print(f"Process ID: {os.getpid()} - Running test_push_to_list_and_pop_from_list")
        self.shared_memory.push_to_list("list1", "a")
        self.shared_memory.push_to_list("list1", "b")
        self.assertEqual(self.shared_memory.pop_from_list("list1"), "a")
        self.assertEqual(self.shared_memory.pop_from_list("list1"), "b")
        self.assertIsNone(self.shared_memory.pop_from_list("list1"))

    def test_shared_memory_across_processes(self):
        def worker_set(shared_memory):
            print(f"Process ID: {os.getpid()} - Running worker_set")
            shared_memory.set_value("count", 1)
            shared_memory.add_value("count", 2)
            shared_memory.push_to_list("numbers", 10)
            shared_memory.push_to_list("numbers", 20)

        def worker_get(shared_memory, queue):
            print(f"Process ID: {os.getpid()} - Running worker_get")
            count = shared_memory.get_value("count")
            number1 = shared_memory.pop_from_list("numbers")
            number2 = shared_memory.pop_from_list("numbers")
            print(f"Process ID: {os.getpid()} - count: {count}, number1: {number1}, number2: {number2}")
            queue.put((count, number1, number2))

        print(f"Process ID: {os.getpid()} - Starting worker_set process")
        p_set = multiprocessing.Process(target=worker_set, args=(self.shared_memory,))
        p_set.start()
        p_set.join()

        queue = multiprocessing.Queue()
        print(f"Process ID: {os.getpid()} - Starting worker_get process")
        p_get = multiprocessing.Process(target=worker_get, args=(self.shared_memory, queue))
        p_get.start()
        p_get.join()

        count, number1, number2 = queue.get()
        self.assertEqual(count, 3)
        self.assertEqual(number1, 10)
        self.assertEqual(number2, 20)

if __name__ == "__main__":
    unittest.main()