"""
Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
Utility file for guenzel_23_inter

- implicit communication only
- periodic tasks 
"""

from math import ceil
from e2eAnalyses.Davare2007 import davare07
import utilities.event_simulator as es

class Schedule_Analyzer():
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


#####
# Schedule construction
#####

def schedule_task_set(ce_chains, task_set, print_status=False):
    """Return the schedule of some task_set.
    ce_chains is a list of ce_chains that will be computed later on.
    We need this to compute latency_upper_bound to determine the additional simulation time at the end.
    Note:
    - In case of error, None is returned."""

    # Preliminary: compute latency_upper_bound
    latency_upper_bound = max([davare07(ce) for ce in ce_chains])

    # Main part: Simulation part
    simulator = es.eventSimulator(task_set)

    # Determination of the variables used to compute the stop
    # condition of the simulation
    max_phase = max(task_set, key=lambda task: task.phase).phase
    max_period = max(task_set, key=lambda task: task.period).period
    hyper_period = task_set.hyperperiod()

    sched_interval = (
        2 * hyper_period
        + max_phase  # interval from paper
        + latency_upper_bound  # upper bound job chain length
        + max_period
    )  # for convenience

    if print_status:
        # Information for end user.
        print("\tNumber of tasks: ", len(task_set))
        print("\tHyperperiod: ", hyper_period)
        number_of_jobs = 0
        for task in task_set:
            number_of_jobs += sched_interval / task.period
        print("\tNumber of jobs to schedule: ", "%.2f" % number_of_jobs)

    # Stop condition: Number of jobs of lowest priority task.
    simulator.dispatcher(int(ceil(sched_interval / task_set[-1].period)))

    # Simulation without early completion.
    schedule = simulator.e2e_result()

    return schedule
