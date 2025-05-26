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
        self._stats_summary = None
        dump_stats = kwargs.get('dump_stats', None)
        self.dump_stats = dump_stats if callable(dump_stats) else None

    def run_step(self):
        if self.collect_at_step ==0:
            return
        self.step += 1
        if self.step % self.collect_at_step == 0:
            self.collect_stats()

        if self.dump_stats is not None:
            for s in self.get_stats(reset=True):
                self.dump_stats(s)


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
                    if( self.debug):
                        print( f"|| stats: {obj} {v}")
                    continue
            else:
                if self.debug:
                    # basic stats with count by class
                    ocls = obj.__class__.__name__
                    v = self._stats_data[self.step].get(ocls, 0)
                    self._stats_data[self.step][ocls] = v + 1


    def get_stats(self,reset=False):
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
        # clear the stats data if reset is True
        if reset:
            self._stats_data = {}
        return s


    def get_stats_summary(self):
        s = []
        summarydata = dict()
        last_entry_by_type = dict()

        for step, stats in self._stats_data.items():
            # store the last entry for each type
            for o_name, o_values in stats.items():
                if o_name not in last_entry_by_type:
                    last_entry_by_type[o_name] = {}
                last_entry_by_type[o_name]['step'] = step
                last_entry_by_type[o_name]['values'] = o_values

        def _calc_stats(v,position):
            if isinstance(v, list):
                values = [i[position] for i in v ]
                count = len(values)
                if values:
                    min_val = min(values)
                    avg_val = sum(values) / count
                    max_val = max(values)
                    return (count, min_val, avg_val, max_val)
            return None

        for o_name in last_entry_by_type.keys():
            # get energy
            count, m, a, x = _calc_stats(last_entry_by_type[o_name]['values'], 0)
            summarydata[o_name] = {
                'last_step': last_entry_by_type[o_name]['step'],
                'count': count,
                'energy_min': m,
                'energy_avg': a,
                'energy_max': x
            }
            count, m, a, x = _calc_stats(last_entry_by_type[o_name]['values'], 1)
            summarydata[o_name].update({
                    'age_min': m,
                    'age_avg': a,
                    'age_max': x
                }
            )
        
        return summarydata
    
    def get_objects_type(self):
        if self._stats_summary is None:
            self._stats_summary = self.get_stats_summary()

        return list(self._stats_summary.keys())
    
    def get_last_step_for_type(self, o_name):
        if self._stats_summary is None:
            self._stats_summary = self.get_stats_summary()

        return self._stats_summary[o_name]['last_step']
    
    def get_count_at_last_step_for_type(self, o_name):
        if self._stats_summary is None:
            self._stats_summary = self.get_stats_summary()

        return self._stats_summary[o_name]['count']
    
    def get_energy_at_last_step_for_type(self, o_name):
        if self._stats_summary is None:
            self._stats_summary = self.get_stats_summary()

        return self._stats_summary[o_name]['energy_min'], self._stats_summary[o_name]['energy_avg'], self._stats_summary[o_name]['energy_max']
            
    def get_age_at_last_step_for_type(self, o_name):
        if self._stats_summary is None:
            self._stats_summary = self.get_stats_summary()

        return self._stats_summary[o_name]['age_min'], self._stats_summary[o_name]['age_avg'], self._stats_summary[o_name]['age_max']
    
    def stats_summary(self):
        all_str=[]
        for t in self.get_objects_type():
            type_str=[]
            type_str.append(str(t))
            type_str.append(self.get_last_step_for_type(t))
            type_str.append(self.get_count_at_last_step_for_type(t))
            type_str.extend(self.get_energy_at_last_step_for_type(t))
            type_str.extend(self.get_age_at_last_step_for_type(t))
            all_str.append(type_str)

        return all_str