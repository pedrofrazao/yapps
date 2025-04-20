import os

class asmObjectStat():
    """Base class for objects that can be monitored for statistics."""
    def __init__(self, nostats=True, **kwargs):
        self.nostats = nostats
        pass

    def stats(self):
        return None

class asmStats():
    def __init__(self, **kwargs):
        self.step = 0
        self.collect_at_step = kwargs.get('collect_at_step', 1)
        self.stats_for_classes = kwargs.get('stats_for_classes', [])
        self._stats_data = {}
        self.debug = kwargs.get('debug', os.environ.get('DEBUG', False))

    def run_step(self):
        if self.collect_at_step ==0:
            return
        self.step += 1
        if self.step % self.collect_at_step == 0:
            self.collect_stats()

    def collect_stats(self):
        self._stats_data[self.step] = {}
        for obj in self.get_objects():
            if isinstance(obj, asmObjectStat):
                if obj.nostats and self.debug is False:
                    continue
                v = obj.stats()
                if v is None:
                    continue
                else:
                    ocls = obj.__class__.__name__
                    l=self._stats_data[self.step].get(ocls,[])
                    l.append(v)
                    self._stats_data[self.step][ocls] = l
                    print( f"|| stats: {obj} {v}")
                    continue
            else:
                if self.debug:
                    # basic stats with count by class
                    ocls = obj.__class__.__name__
                    v = self._stats_data[self.step].get(ocls, 0)
                    self._stats_data[self.step][ocls] = v + 1

    def get_stats(self):
        s = []
        for step, stats in self._stats_data.items():
            for k, v in stats.items():
                if isinstance(v, list):
                    for i in v:
                        olist=[step,k]
                        olist.extend(i)
                        s.append( olist )
                else:
                    s.append([step,k,v] )
        return s