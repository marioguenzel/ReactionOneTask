#!/usr/bin/env python3

'''
Basis from https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed/blob/master/e2e/tasks/taskset.py
'''

import math


class TaskSet:
    """A set of Task-Objects."""

    # Assumption: Task set ordered by priority
    # Lower index = Higher Priority

    def __init__(self, *args):
        """Input: Task-Objects"""
        self._lst = list(args)

    def __len__(self):
        return self._lst.__len__()

    def __getitem__(self, item):
        return self._lst.__getitem__(item)

    def __setitem__(self, key, value):
        self._lst.__setitem__(key, value)

    def __delitem__(self, key):
        self._lst.__delitem__(key)

    def __iter__(self):
        yield from self._lst

    def append(self, obj):
        self._lst.append(obj)

    def prio(self, task):
        """Priority of a task"""
        return self._lst.index(task)

    def higher_prio(self, task1, task2):
        """task1 has higher prio than task2."""
        return self.prio(task1) < self.prio(task2)

    def utilization(self):
        return sum(task.utilization() for task in self)

    def communication(self):
        if all('implicit' == task.communication_policy for task in self):
            return 'implicit'
        elif all('LET' == task.communication_policy for task in self):
            return 'LET'
        else:
            return 'mixed'

    def check_feature(self, feature):
        assert feature in ['comm', 'ex', 'rel', 'dl']
        # First value
        val = getattr(self[0], feature).type

        if all(val == getattr(task, feature).type for task in self):
            return val
        else:
            return 'mixed'

    def print(self, length=True, utilization=False, communication=False, execution=False, release=False,
              deadline=False):
        printstr = ''
        printstr += self.__str__() + '\t'
        if length is True:
            printstr += f'length: {len(self)}, '
        if utilization is True:
            printstr += f'utilization: {self.utilization()}, '
        if communication is True:
            printstr += f"communication: {self.check_feature('comm')}, "
        if execution is True:
            printstr += f"execution: {self.check_feature('ex')}, "
        if release is True:
            printstr += f"release: {self.check_feature('rel')}, "
        if deadline is True:
            printstr += f"deadline: {self.check_feature('dl')}, "
        print(printstr)

    def print_tasks(self):
        for task in self:
            task.print()

    def compute_wcrts(self):
        """Compute wcrts by TDA."""
        self.wcrts = dict()
        for idx in range(len(self._lst)):
            self.wcrts[self._lst[idx]] = tda(self._lst[idx], self._lst[:idx])

    def hyperperiod(self):
        """Task set hyperperiod."""
        return math.lcm(*[task.period for task in self._lst])

    def max_phase(self):
        """Maximal phase of the task set."""
        return max([task.phase for task in self._lst])

    def sort_dm(self):
        """Sort by deadline."""
        self._lst.sort(key=lambda x: x.deadline)


def transform(taskset, precision=10000000):
    """"Multiplies the following values for each task with precision and makes integer.
    (Important for analyses with hyperperiod)."""
    transform_arguments = {
        'rel': ['maxiat', 'miniat', 'period', 'phase'],
        'dl': ['dl'],
        'ex': ['wcet', 'bcet'],
        'comm': []
    }

    for task in taskset:
        # get all relevant values:
        task_vals = dict()
        for targ in transform_arguments:
            if hasattr(task, targ):
                task_feat = getattr(task, targ)
                task_vals[targ] = dict()
                for targarg in transform_arguments[targ]:
                    if hasattr(task_feat, targarg):
                        task_vals[targ][targarg] = getattr(task_feat, targarg)

        # Transform and set relevant values
        for targ in task_vals:
            feat = getattr(task, targ)
            for targarg in task_vals[targ]:
                if task_vals[targ][targarg] is not None:
                    setattr(feat, targarg,
                            int(task_vals[targ][targarg] * precision))


def tda(task, hp_tasks):
    """Implementation of TDA to calculate worst-case response time.
    Source:
    https://github.com/kuanhsunchen/MissRateSimulator/blob/master/TDA.py
    """
    c = task.wcet  # WCET
    r = c  # WCRT
    while True:
        i = 0  # interference
        for itask in hp_tasks:
            i = i + _workload(itask.min_iat, itask.wcet, r)
        if r < i + c:
            r = i + c
        else:
            return r


def _workload(period, wcet, time):
    """Workload function for TDA.
    Help function for tda().
    """
    return wcet * math.ceil(float(time) / period)


if __name__ == '__main__':
    """Debug."""
    from tasks.task import Task

    tset = (
        Task(release='periodic', period=10, phase=1, execution='bcwc', wcet=1 / 3, communication='LET'),
        Task(release='periodic', period=20, phase=10, execution='bcwc', wcet=1 / 2, communication='implicit'),
        Task(release='periodic', period=50, phase=5, execution='bcwc', wcet=1 / 7, communication='LET')
    )

    ts = TaskSet(*tset)
    breakpoint()
