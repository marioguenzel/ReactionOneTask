"""
Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter

Utility file for analysis methods that need a schedule
"""

import math
from multiprocessing import Pool
from e2eAnalyses.Davare2007 import davare07
import utilities.event_simulator as es



# Helper function
def flattened_cec_tuple_list(cecs):
    if isinstance(cecs[0], tuple):
        flattened_list = []
        for cec_tuple in cecs:
            for cec in list(cec_tuple):
                flattened_list.append(cec)
        return flattened_list
    else:
        return cecs


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
        lst = self.schedule[task.id]  # list that has the read-even minimum
        # choose read-event from list
        return self._get_entry(nmb, lst, task)[0]

    def finish(self, task, nmb):
        '''returns the upper bound on read-event of the nbm-th job of a task.'''
        lst = self.schedule[task.id]  # list that has the write-even minimum
        # choose write-event from list
        return self._get_entry(nmb, lst, task)[1]


#####
# Schedule construction
#####

def schedule_task_set(ce_chains, task_set):
    """Return the schedules of some task_set.
    ce_chains is a list of ce_chains that will be computed later on.
    We need this to compute latency_upper_bound to determine the additional simulation time at the end.
    Note:
    - In case of error, None is returned."""

    separate_bcet = task_set[0].bcet != task_set[0].wcet

    # try:
    # Preliminary: compute latency_upper_bound
    latency_upper_bound = max([davare07(ce) for ce in ce_chains])

    # Main part: Simulation part for wcet/bcet taskset
    simulator_wcet = es.eventSimulator(task_set, False)
    if separate_bcet:
        simulator_bcet = es.eventSimulator(task_set, True)

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

    # Stop condition: Number of jobs of lowest priority task.
    simulator_wcet.dispatcher(int(math.ceil(sched_interval / task_set[-1].period)))
    if separate_bcet:
        simulator_bcet.dispatcher(int(math.ceil(sched_interval / task_set[-1].period)))

    # Simulation without early completion.
    schedules = dict()
    schedules['wcet'] = simulator_wcet.e2e_result()
    if separate_bcet:
        schedules['bcet'] = simulator_bcet.e2e_result()
    else:
        schedules['bcet'] = schedules['wcet']


    # except Exception as e:
    #     schedules = None

    return (task_set.id, schedules)


def compute_all_schedules(cause_effect_chains, number_of_threads):

    # cecs can be a list of tuples in case of inteconnected cecs
    # and have to be flattened first to be scheduled
    cause_effect_chains = flattened_cec_tuple_list(cause_effect_chains)

    taskset_cecs = dict()
    for cause_effect_chain in cause_effect_chains:
        if cause_effect_chain.base_ts in  taskset_cecs.keys():
            taskset_cecs[cause_effect_chain.base_ts].append(cause_effect_chain)
        else:
            taskset_cecs[cause_effect_chain.base_ts] = [cause_effect_chain]

    # [([ce_chain], taskset), ([ce_chain], taskset), ([ce_chain], taskset), ...]
    argument_list = []
    for taskset in taskset_cecs.keys():
        argument_list.append((taskset_cecs[taskset], taskset))

    with Pool(number_of_threads) as pool:
        schedule_list = pool.starmap(schedule_task_set, argument_list)

    tasksets = dict()
    for taskset in taskset_cecs.keys():
        tasksets[taskset.id] = taskset

    # schedules :: [(taskset, schedule)]
    for taskset_id, schedule in schedule_list:
        assert taskset_id in tasksets.keys()
        tasksets[taskset_id].schedules = schedule