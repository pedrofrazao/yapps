import multiprocessing
import ctypes

class SharedMemoryManager:
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.shared_dict = self.manager.dict()
        self.shared_lists = self.manager.dict()

    def set_value(self, key, value):
        self.shared_dict[key] = value

    def get_value(self, key):
        return self.shared_dict.get(key, None)

    def add_value(self, key, value):
        if key in self.shared_dict:
            self.shared_dict[key] += value
        else:
            self.shared_dict[key] = value

    def push_to_list(self, key, value):
        if key not in self.shared_lists:
            self.shared_lists[key] = self.manager.list()
        self.shared_lists[key].append(value)

    def pop_from_list(self, key):
        if key in self.shared_lists and len(self.shared_lists[key]) > 0:
            return self.shared_lists[key].pop(0)
        return None

# Example usage
if __name__ == "__main__":
    def worker(shared_memory):
        shared_memory.set_value("count", 1)
        shared_memory.add_value("count", 2)
        shared_memory.push_to_list("numbers", 10)
        shared_memory.push_to_list("numbers", 20)
        print("Worker: count =", shared_memory.get_value("count"))
        print("Worker: numbers =", shared_memory.pop_from_list("numbers"))

    shared_memory = SharedMemoryManager()
    p = multiprocessing.Process(target=worker, args=(shared_memory,))
    p.start()
    p.join()

    print("Main: count =", shared_memory.get_value("count"))
    print("Main: numbers =", shared_memory.pop_from_list("numbers"))