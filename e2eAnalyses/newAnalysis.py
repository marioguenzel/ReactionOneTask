"""
Analyses from Guenzel et al.:
Timing Analysis of Asynchronized Distributed Cause-Effect Chains (2021)
Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains (2023)

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
and https://github.com/tu-dortmund-ls12-rt/end-to-end
"""


import math
import itertools
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


#####
# Job Definition
#####


class Job:
    """A job."""

    def __init__(self, task=None, number=None):
        """Create (number)-th job of a task (task).
        Assumption: number starts at 0. (0=first job)"""
        self.task = task
        self.number = number

    def __str__(self):
        return f"({self.task}, {self.number})"


#####
# Job chain definition
#####


class JobChain(list):
    """A chain of jobs."""

    def __init__(self, *jobs):
        """Create a job chain with jobs *jobs."""
        super().__init__(jobs)

    def __str__(self, no_braces=False):
        return "[ " + " -> ".join([str(j) for j in self]) + " ]"


class FwJobChain(JobChain):
    """Immediate forward job chain."""

    def __init__(self, ce_chain: CEChain, number: int, ana):
        """Create (number)-th immediate forward job chain. (under LET)"""
        self.number = number  # number of forward job chain
        self.ana = ana

        if len(ce_chain) == 0:
            super().__init__()
            return

        abstr = []
        abstr.append(number)  # first entry

        for task, next_task in zip(ce_chain[:-1], ce_chain[1:]):
            abstr.append(ana.find_next_fw(
                task, next_task, abstr[-1]))  # intermediate entries

        self.abstr = abstr

        job_lst = []
        for i in range(len(abstr)):
            job = Job(
                ce_chain[i],
                abstr[i],
            )
            job_lst.append(job)

        # Make job chain
        super().__init__(*job_lst)


class BwJobChain(JobChain):
    """Immediate backward job chain."""

    def __init__(self, ce_chain: CEChain, number: int, ana):
        """Create (number)-th immediate backward job chain. (under LET)"""
        self.number = number  # number of backward job chain
        self.ana = ana

        if len(ce_chain) == 0:
            super().__init__()
            return


        abstr = []
        abstr.append(number)  # last entry

        for task, prev_task in zip(ce_chain[::-1][:-1], ce_chain[::-1][1:]):
            idx = ana.find_next_bw(
                task, prev_task, abstr[-1])
            abstr.append(idx)  # intermediate entries

            if idx == -1:  # check if incomplete
                break

        # Turn around the chain
        abstr = abstr[::-1]

        self.abstr = abstr

        job_lst = []
        for i in range(len(abstr)):
            job = Job(
                ce_chain[i],
                abstr[i],
            )
            job_lst.append(job)

        # Make job chain
        super().__init__(*job_lst)

        # check if complete
        self.complete = job_lst[0].number >= 0


class PartitionedJobChain:
    """A partitioned job chain."""

    def __init__(self, part, chain, number, ana):
        """Create a partitioned job chain.
        - part = where is the partioning
        - chain = cause-effect chain
        - number = which chain"""
        assert 0 <= part < len(chain), "part is out of possible interval"
        self.bw = BwJobChain(chain[: part + 1], number, ana)
        self.fw = FwJobChain(chain[part:], number + 1, ana)  # forward job chain part
        self.complete = self.bw.complete  # complete iff bw chain complete
        self.base_ce_chain = chain
        self.ana = ana

    def __str__(self):
        entries = [self.bw.__str__(no_braces=True), self.fw.__str__(no_braces=True)]
        return "[ " + " / ".join(entries) + " ]"

    def ell(self):
        """Length of the partitioned job chain, more precisely l() function from the paper."""
        # return self.ana.len_abstr(self.fw.abstr, self.fw[-1].task, self.fw[0].task) + self.ana.len_abstr(self.bw.abstr, self.bw[-1].task, self.bw[0].task)
        return self.ana.wemax(self.fw[-1].task, self.fw.abstr[-1]) - self.ana.remin(self.bw[0].task, self.bw.abstr[0])


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
        task.wcet = rat * task.wcet
        task.bcet = rat * task.bcet
    return new_task_set


#####
# Find Fi
#####

def find_fi(ce_chain: CEChain, ana) -> list[int]:
    """List of Fi values."""
    # one forward chain
    fc = FwJobChain(ce_chain, 0, ana)
    F = fc[-1].number
    # one backward chain
    bc = BwJobChain(ce_chain, F, ana)
    Fi = [job.number for job in bc]
    return Fi

#####
# New analysis
#####

def our_mrt_mRda_lst(chain, bcet, wcet):

    # make schedules and store in dictionary
    schedules_todo = [bcet]
    if wcet not in schedules_todo:
        schedules_todo.append(wcet)

    schedules = dict()  # schedules
    ts_lst = dict()  # task sets

    for et in schedules_todo:
        if et == 1.0:
            ts_et = chain.base_ts  # otherwise tasks in the chain can not be allocated
        else:
            ts_et = change_taskset_bcet(chain.base_ts, et)  # task set with certain execution time
        if et not in chain.base_ts.schedules.keys():
            if et != 0:  # the dispatcher can only handle execution != 0
                sched_et = schedule_task_set(
                    [chain], ts_et, print_status=True
                )  # schedule with certain execution time
            else:
                sched_et = a_our.execution_zero_schedule(ts_et)
            chain.base_ts.schedules[et] = sched_et
        else:
            sched_et = chain.base_ts.schedules[et]
        schedules[et] = sched_et
        ts_lst[et] = ts_et

    ana = a_our.re_we_analyzer(schedules[bcet], schedules[wcet], chain.base_ts.hyperperiod())
    
    # Construct F_i
    Fi = find_fi(chain, ana)

    # find analysis interval
    analysis_end = 2 * chain.base_ts.hyperperiod() + chain.base_ts.max_phase()

    # choose point for partitioning
    # just choose the task with highest period
    periods = [tsk.period for tsk in chain]
    part = periods.index(max(periods))

    # construct partitioned chains
    part_chains = []
    for number in itertools.count(start=Fi[part]):
        pc = PartitionedJobChain(part, chain, number, ana)
        if ana.remin(pc.bw[0].task, pc.bw[0].number) <= analysis_end:
            part_chains.append(pc)
        else:
            break

    assert all(pc.complete for pc in part_chains)
    return max([pc.ell() for pc in part_chains], default=0) #   TODO fixme


def newAna(chain):
    latency = our_mrt_mRda_lst(chain, 1.0, 1.0)
    return latency



