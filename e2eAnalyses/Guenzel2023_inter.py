"""
Analyses from Guenzel et al.:
Timing Analysis of Asynchronized Distributed Cause-Effect Chains (2021)
Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains (2023)

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
and https://github.com/tu-dortmund-ls12-rt/end-to-end
"""


import math
from tasks.task import Task
from tasks.taskset import TaskSet
from cechains.chain import CEChain
import utilities.event_simulator as es
import utilities.analyzer_our as a_our
from e2eAnalyses.Davare2007 import davare07


debug_flag = False  # flag to have breakpoint() when errors occur

# Note:
# lst_flat = (ce, ts, sched)
# lst = ([ces], ts, sched)


def schedule_task_set(ce_chains, task_set, print_status=False):
    """Return the schedule of some task_set.
    ce_chains is a list of ce_chains that will be computed later on.
    We need this to compute latency_upper_bound to determine the additional simulation time at the end.
    Note:
    - In case of error, None is returned."""

    try:
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
        simulator.dispatcher(int(math.ceil(sched_interval / task_set[-1].period)))

        # Simulation without early completion.
        schedule = simulator.e2e_result()

    except Exception as e:
        print(e)
        if debug_flag:
            breakpoint()
        schedule = None

    return schedule


def change_taskset_bcet(task_set, rat):
    """Copy task set and change the wcet/bcet of each task by a given ratio."""
    new_task_set = TaskSet(*[task.copy() for task in task_set])
    for task in new_task_set:
        task.wcet = math.ceil(rat * task.wcet)
        task.bcet = math.ceil(rat * task.bcet)
    # Note: ceiling function makes sure there is never execution of 0
    return new_task_set


def our_mrt_mRda_lst(lst_ce_ts, bcet_lst, wcet=1.0):
    """lst_ce_ts[0] = list of ce-chains, lst_ce_ts[1] = task set, bcet_lst = [0.0, 0.3, 0.7, 1.0]"""
    ce_lst = lst_ce_ts[0]
    ts = lst_ce_ts[1]
    wcet = 1.0

    # make schedules and store in dictionary
    schedules_todo = bcet_lst
    if wcet not in schedules_todo:
        schedules_todo.append(wcet)

    schedules = dict()  # schedules
    ts_lst = dict()  # task sets

    for et in schedules_todo:
        if et == 1.0:
            ts_et = ts  # otherwise tasks in the chain can not be allocated
        else:
            ts_et = change_taskset_bcet(ts, et)  # task set with certain execution time
        if et not in ts.schedules.keys():
            if et != 0:  # the dispatcher can only handle execution != 0
                sched_et = schedule_task_set(
                    ce_lst, ts_et, print_status=True
                )  # schedule with certain execution time
            else:
                sched_et = a_our.execution_zero_schedule(ts_et)
            ts.schedules[et] = sched_et
        else:
            sched_et = ts.schedules[et]
        schedules[et] = sched_et
        ts_lst[et] = ts_et

    # do analysis for certain schedules
    results = []  # results

    for ce in ce_lst:
        results_ce = dict()
        for bcet in bcet_lst:
            results_ce[bcet] = dict()
            # breakpoint()
            ce_mrt = a_our.max_reac_local(
                ce, ts_lst[wcet], schedules[wcet], ts_lst[bcet], schedules[bcet]
            )
            ce_mda, ce_mrda = a_our.max_age_local(
                ce, ts_lst[wcet], schedules[wcet], ts_lst[bcet], schedules[bcet]
            )
            results_ce[bcet]["mrt"] = ce_mrt
            results_ce[bcet]["mda"] = ce_mda
            results_ce[bcet]["mrda"] = ce_mrda
        results.append(results_ce)
    return results


# single ecu
def guenzel_23_local_mrt(chain):
    lst_ce_ts = [[chain], chain.base_ts]
    latencies = our_mrt_mRda_lst(lst_ce_ts, [1.0], 1.0)
    return latencies[0][1.0]['mrt']


def guenzel_23_local_mda(chain):
    lst_ce_ts = [[chain], chain.base_ts]
    latencies = our_mrt_mRda_lst(lst_ce_ts, [1.0], 1.0)
    return latencies[0][1.0]['mda']


def guenzel_23_local_mrda(chain):
    lst_ce_ts = [[chain], chain.base_ts]
    latencies = our_mrt_mRda_lst(lst_ce_ts, [1.0], 1.0)
    return latencies[0][1.0]['mrda']


# inter ecu analyses
def guenzel_23_inter_mrt(*local_chains):
    inter_chain = list(local_chains)
    latency = 0
    for local_chain in inter_chain:
        latency+=guenzel_23_local_mrt(local_chain)
    return latency


def guenzel_23_inter_mrda(*local_chains):
    inter_chain = list(local_chains)
    latency = 0
    for local_chain in inter_chain:
        latency+=guenzel_23_local_mrda(local_chain)
    return latency
