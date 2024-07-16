"""End-to-End (e2e) Analysis by Becker et al.
https://doi.org/10.1016/j.sysarc.2017.09.004
https://doi.org/10.1109/RTCSA.2016.41

Implementation is copied from https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
- only minor adjustments

"""
from cechains.chain import CEChain
from tasks.task import Task
from math import ceil
from e2eAnalyses.Davare2007 import davare07
from utilities.schedule_analyzer import schedule_analyzer
import utilities.event_simulator as es
from enum import Enum

Init_Type = Enum(
    'Init_Type',
    'NO_INFORMATION RESPONSE_TIMES SCHED_TRACE LET'
)

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


class DPT:

    def __init__(self, chain, occurrence, init_type):
        self.chain = chain
        self.init_type = init_type

        if init_type == Init_Type.SCHED_TRACE:
            if 1.0 not in chain.base_ts.schedules.keys():
                schedule = schedule_task_set([chain], chain.base_ts, print_status=True)
                chain.base_ts.schedules[1.0] = schedule
            self.schedule = chain.base_ts.schedules[1.0]
            self.ana = schedule_analyzer(self.schedule, chain.base_ts.hyperperiod())

        self.occurrences = self.build_tree(0, occurrence)


    # ===== Help functions =====
    def Rmin(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return tsk.phase + idx * tsk.period
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return tsk.phase + idx * tsk.period
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.ana.start(tsk, idx)
        elif self.init_type == Init_Type.LET:
            return tsk.phase + idx * tsk.period


    def Rmax(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return self.Rmin(tsk, idx) + tsk.period - tsk.wcet
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return self.Rmin(tsk, idx) + self.chain.base_ts.wcrts[tsk] - tsk.wcet
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.Rmin(tsk, idx)
        elif self.init_type == Init_Type.LET:
            return self.Rmin(tsk, idx)


    def Dmin(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return self.Rmin(tsk, idx) + tsk.wcet
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return self.Rmin(tsk, idx) + tsk.wcet
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.ana.finish(tsk, idx)
        elif self.init_type == Init_Type.LET:
            return self.Rmin(tsk, idx) + tsk.period


    def Dmax(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return self.Rmax(tsk, idx + 1) + tsk.wcet
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return self.Rmax(tsk, idx + 1) + tsk.wcet
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.ana.finish(tsk, idx+1)
        elif self.init_type == Init_Type.LET:
            return self.Dmin(tsk, idx) + tsk.period


    def build_tree(self, current_position: int, current_job_idx: int):
        if current_position + 1 >= self.chain.length():
            return [current_job_idx]

        current_task: Task = self.chain[current_position]
        next_task: Task = self.chain[current_position + 1]

        # With this index the below property is safely fulfilled:
        next_job_idx = (
            ceil((self.Dmax(current_task, current_job_idx) - next_task.phase) / next_task.period)
            - 1
        )

        while not self.Rmin(next_task, next_job_idx) < self.Dmax(current_task, current_job_idx):
            next_job_idx = next_job_idx - 1

        next_job_idx = max(next_job_idx, 0)

        # Note that in https://doi.org/10.1016/j.sysarc.2017.09.004 it is not specified what happens if there is no reachable job due to large phase of next_task.
        # We assume that in that case the build_tree function returns a shorter tree than expected.
        if self.Rmin(next_task, next_job_idx) >= self.Dmax(current_task, current_job_idx):
            # No reachable job
            return []

        while self.Rmin(next_task, next_job_idx + 1) < self.Dmax(current_task, current_job_idx):
            next_job_idx = next_job_idx + 1

        return [current_job_idx] + self.build_tree(current_position + 1, next_job_idx)
    
    
    def length(self):
        return len(self.occurrences)


    def age(self):
        return self.Rmax(self.chain[self.length()-1], self.occurrences[self.length()-1]) + self.chain[self.length()-1].wcet - self.Rmin(self.chain[0], self.occurrences[0])


# ===== Analysis =====
def beckerFast(chain: CEChain, init_type):
    hp = chain.hyperperiod()
    max_phase = chain.max_phase()
    ages = []
    ind_job = 0

    while chain[0].period * ind_job <= hp + max_phase:
        tree = DPT(chain, ind_job, init_type)
        if tree.length() == chain.length():
            ages.append(tree.age())
        ind_job = ind_job + 1

    return max(ages)


def beckerFast_NO_INFORMATION(chain):
    return beckerFast(chain, Init_Type.NO_INFORMATION)

def beckerFast_RESPONSE_TIMES(chain):
    return beckerFast(chain, Init_Type.RESPONSE_TIMES)

def beckerFast_SCHED_TRACE(chain):
    return beckerFast(chain, Init_Type.SCHED_TRACE)

def beckerFast_LET(chain):
    return beckerFast(chain, Init_Type.LET)
