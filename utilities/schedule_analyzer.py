"""
Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
Utility file for guenzel_23_inter

- implicit communication only
- periodic tasks 
"""


class schedule_analyzer():
    def __init__(self, schedule, hyperperiod):
        self.schedule = schedule
        self.hyperperiod = hyperperiod

    def _get_entry(self, nmb, lst, tsk):
        '''get nmb-th entry of the list lst with task tsk.'''
        if nmb < 0:
        # Case: index too low, has to be made larger
            return (0,0)
            # check some hyperperiods later
            # make new_nmb an integer value
            new_nmb = nmb
            counter = 0
            while new_nmb < len(lst):
                div, rem = divmod(self.hyperperiod, tsk.period)
                assert rem == 0
                new_nmb = new_nmb + div
                counter += 1
            # add counter hyperperiods
            # TODO this is not very efficient since we need the values several times.
            return [self.hyperperiod * counter + entry for entry in lst[new_nmb]]
        # Case: index too high, has to be made smaller 
        # TODO not sure if this is a good idea since the last entries could be wrong depending on the implementation of the scheduler ...
        elif nmb >= len(lst):
            # check some hyperperiods earlier
            # make new_nmb an integer value
            new_nmb = nmb
            counter = 0
            while new_nmb >= len(lst):
                div, rem = divmod(self.hyperperiod, tsk.period)
                assert rem == 0
                new_nmb = new_nmb - div
                counter += 1
            # add counter hyperperiods
            # TODO this is not very efficient since we need the values several times.
            return [self.hyperperiod * counter + entry for entry in lst[new_nmb]]
        else:  # Case: entry can be used
            try:
                return lst[nmb]
            except:
                breakpoint()

    def start(self, task, nmb):
        '''returns the upper bound on read-event of the nbm-th job of a task.'''
        lst = self.schedule[task]  # list that has the read-even minimum
        # choose read-event from list
        return self._get_entry(nmb, lst, task)[0]

    def finish(self, task, nmb):
        '''returns the upper bound on read-event of the nbm-th job of a task.'''
        lst = self.schedule[task]  # list that has the write-even minimum
        # choose write-event from list
        return self._get_entry(nmb, lst, task)[1]
