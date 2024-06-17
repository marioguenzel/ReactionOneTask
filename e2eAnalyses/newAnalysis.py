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
from cechains.chain import CEChain
import utilities.event_simulator as es
import utilities.analyzer_our as a_our
from e2eAnalyses.Davare2007 import davare07


#####
# Job Definition
#####


class Job:
    """A job."""

    def __init__(self, task=None, number=None, start=None, finish=None):
        """Create (number)-th job of a task (task).
        Assumption: number starts at 0. (0=first job)"""
        self.task = task
        self.number = number
        self.start = start
        self.finish = finish

    def __str__(self):
        return f"({self.task}, {self.number})"


#####
# Help functions for imolicit communication
#####


def impl_we(job: Job):
    """Latest possible write-event of job under implicit communication"""
    return job.finish + job.task.period * job.number


def impl_re(job: Job):
    """Earliest possible read-event of job under implicit communication"""
    return job.start + job.task.period * job.number


def let_re_geq(time, task: Task):
    """Number of earliest job of (task) with read-event at or after (time)"""
    n = max(math.floor((time - task.phase) / task.period), 0)
    
    return max(math.ceil((time - task.phase) / task.period), 0)


def let_we_leq(time, task: Task):
    """Number of latest job of (task) with write-event at or before (time)"""
    return math.floor((time - task.phase - task.deadline) / task.period)



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

    def ell(self):
        """length of a job chain"""
        return impl_we(self[-1]) - impl_re(self[0])


class FwJobChain(JobChain):
    """Immediate forward job chain."""

    def __init__(self, ce_chain: CEChain, number: int, schedule_wcet: dict, schedule_bcet: dict):
        """Create (number)-th immediate forward job chain. (under LET)"""
        self.number = number  # number of forward job chain

        if len(ce_chain) == 0:
            super().__init__()
            return
        
        first_job = Job(ce_chain[0], number, schedule_bcet[ce_chain[0]][0][0], schedule_wcet[ce_chain[0]][0][1])
        job_lst = [first_job]

        # next jobs
        for task in ce_chain[1:]:
            # find next job
            next_job_number = max(math.floor((impl_we(job_lst[-1]) - task.phase) / task.period), 0)

            next_job = Job(task, next_job_number, schedule_bcet[task][0][0], schedule_wcet[task][0][1])
            if next_job.start < impl_we(job_lst[-1]):
                next_job = Job(task, next_job_number+1, schedule_bcet[task][0][0], schedule_wcet[task][0][1])

            # add job to chain
            job_lst.append(next_job)

        # Make job chain
        super().__init__(*job_lst)


class BwJobChain(JobChain):
    """Immediate backward job chain."""

    def __init__(self, ce_chain: CEChain, number: int, schedule_wcet: dict, schedule_bcet: dict):
        """Create (number)-th immediate backward job chain. (under LET)"""
        self.number = number  # number of backward job chain

        if len(ce_chain) == 0:
            super().__init__()
            return

        last_job = Job(ce_chain[-1], number, schedule_bcet[ce_chain[-1]][0][0], schedule_wcet[ce_chain[-1]][0][1])
        job_lst = [last_job]

        # previous jobs
        for task in ce_chain[0:-1][::-1]:  # backwards except the last
            # find previous job
            previous_job_number = 1
            (re, we) = schedule_bcet[task][0]
            while we + task.period < impl_re(job_lst[-1]):
                previous_job_number += 1
                we += task.period

            previous_job = Job(task, previous_job_number, schedule_bcet[task][0][0], schedule_wcet[task][0][1])

            # add job to chain
            job_lst.insert(0, previous_job)

        # Make job chain
        super().__init__(*job_lst)

        # check if complete
        self.complete = job_lst[0].number >= 0


class PartitionedJobChain:
    """A partitioned job chain."""

    def __init__(self, part, chain, number, schedule_wcet, schedule_bcet):
        """Create a partitioned job chain.
        - part = where is the partioning
        - chain = cause-effect chain
        - number = which chain"""
        assert 0 <= part < len(chain), "part is out of possible interval"
        self.bw = BwJobChain(chain[: part + 1], number, schedule_wcet, schedule_bcet)
        self.fw = FwJobChain(chain[part:], number + 1, schedule_wcet, schedule_bcet)  # forward job chain part
        self.complete = self.bw.complete  # complete iff bw chain complete
        self.base_ce_chain = chain

    def __str__(self):
        entries = [self.bw.__str__(no_braces=True), self.fw.__str__(no_braces=True)]
        return "[ " + " / ".join(entries) + " ]"

    def ell(self):
        """Length of the partitioned job chain, more precisely l() function from the paper."""
        return impl_we(self.fw[-1]) - impl_re(self.bw[0])


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
    new_task_set = [task.copy() for task in task_set]
    for task in new_task_set:
        task.wcet = math.ceil(rat * task.wcet)
        task.bcet = math.ceil(rat * task.bcet)
    # Note: ceiling function makes sure there is never execution of 0
    return new_task_set


#####
# Find Fi
#####

def find_fi(ce_chain: CEChain, schedule_wcet: dict, schedule_bcet: dict) -> list[int]:
    """List of Fi values."""
    # one forward chain
    fc = FwJobChain(ce_chain, 0, schedule_wcet, schedule_bcet)
    F = fc[-1].number
    # one backward chain
    bc = BwJobChain(ce_chain, F, schedule_wcet, schedule_bcet)
    Fi = [job.number for job in bc]
    return Fi

#####
# New analysis
#####

def our_mrt_mRda_lst(chain, bcet_lst, wcet=1.0):
    """lst_ce_ts[0] = list of ce-chains, lst_ce_ts[1] = task set, bcet_lst = [0.0, 0.3, 0.7, 1.0]"""
    wcet = 1.0

    # make schedules and store in dictionary
    schedules_todo = bcet_lst
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

    
    # Construct F_i
    Fi = find_fi(chain, schedules[wcet], schedules[wcet])

    # find analysis interval
    analysis_end = 6 * chain.base_ts.hyperperiod() + chain.base_ts.max_phase()

    # choose point for partitioning
    # just choose the task with highest period
    periods = [tsk.period for tsk in chain]
    part = periods.index(max(periods))

    # construct partitioned chains
    part_chains = []
    for number in itertools.count(start=Fi[part]):
        pc = PartitionedJobChain(part, chain, number, schedules[wcet], schedules[wcet])
        if impl_re(pc.bw[0]) <= analysis_end:
            part_chains.append(pc)
        else:
            break

    assert all(pc.complete for pc in part_chains)
    return max([pc.ell() for pc in part_chains])

    # ce_mrt = a_our.max_reac_local(
    #     CEChain(*list(chain[part:]), base_ts=chain.base_ts), ts_lst[wcet], schedules[wcet], ts_lst[wcet], schedules[wcet]
    # )

    # ce_mda, ce_mrda = a_our.max_age_local(
    #     CEChain(*list(chain[:part+1]), base_ts=chain.base_ts), ts_lst[wcet], schedules[wcet], ts_lst[wcet], schedules[wcet]
    # )

    # return ce_mrda + ce_mrt




def newAna(chain):
    latency = our_mrt_mRda_lst(chain, [1.0], 1.0)
    return latency



