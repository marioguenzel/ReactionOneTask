"""Analysis applied in the evaluation.
Assumptions:
- LET
- periodic"""
import itertools
import math
from cechains.chain import CEChain
import timeit
from tasks.task import Task


#####
# Job
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
# Help functions for LET communication
#####


def let_we(job: Job):
    """Write-event of job under LET."""
    return job.task.phase + job.task.period * job.number + job.task.deadline


def let_re(job: Job):
    """Read-event of job under LET."""
    return job.task.phase + job.task.period * job.number


def let_re_geq(time, task: Task):
    """Number of earliest job with read-event of (task) at or after (time)."""
    return max(math.ceil((time - task.phase) / task.period), 0)


def let_re_gt(time, task: Task):
    """Number of earliest job with read-event of (task) after (time)."""
    return max(math.floor((time - task.phase) / task.period) + 1, 0)


def let_we_leq(time, task: Task):
    """Number of latest job with write-event of (task) at or before (time)."""
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
        return let_we(self[-1]) - let_re(self[0])


class FwJobChain(JobChain):
    """Immediate forward job chain."""

    def __init__(self, ce_chain: CEChain, number: int):
        """Create (number)-th immediate forward job chain. (under LET)"""
        self.number = number  # number of forward job chain

        if len(ce_chain) == 0:
            super().__init__()
            return

        # first job
        job_lst = [Job(ce_chain[0], number)]

        # next jobs
        for tsk in ce_chain[1:]:
            # find next job
            next_job_number = let_re_geq(let_we(job_lst[-1]), tsk)

            # add job to chain
            job_lst.append(Job(tsk, next_job_number))

        # Make job chain
        super().__init__(*job_lst)


class BwJobChain(JobChain):
    """Immediate backward job chain."""

    def __init__(self, ce_chain: CEChain, number: int):
        """Create (number)-th immediate backward job chain. (under LET)"""
        self.number = number  # number of backward job chain

        if len(ce_chain) == 0:
            super().__init__()
            return

        # last job
        job_lst = [Job(ce_chain[-1], number)]

        # previous jobs jobs
        for tsk in ce_chain[0:-1][::-1]:  # backwards except the last
            # find previous job
            previous_job_number = let_we_leq(let_re(job_lst[0]), tsk)

            # add job to chain
            job_lst.insert(0, Job(tsk, previous_job_number))

        # Make job chain
        super().__init__(*job_lst)

        # check if complete
        self.complete = job_lst[0].number >= 0


#####
# Find Fi
#####

def find_fi(ce_chain: CEChain) -> list[int]:
    """List of Fi values."""
    # one forward chain
    fc = FwJobChain(ce_chain, 0)
    F = fc[-1].number
    # one backward chain
    bc = BwJobChain(ce_chain, F)

    Fi = [job.number for job in bc]
    return Fi


#####
# Our analysis
#####

class PartitionedJobChain:
    """A partitioned job chain."""

    def __init__(self, part, chain, number):
        """Create a partitioned job chain.
        - part = where is the partioning
        - chain = cause-effect chain
        - number = which chain"""
        assert 0 <= part < len(chain), "part is out of possible interval"
        self.bw = BwJobChain(chain[: part + 1], number)
        self.fw = FwJobChain(chain[part:], number + 1)  # forward job chain part
        self.complete = self.bw.complete  # complete iff bw chain complete
        self.base_ce_chain = chain

    def __str__(self):
        entries = [self.bw.__str__(no_braces=True), self.fw.__str__(no_braces=True)]
        return "[ " + " / ".join(entries) + " ]"

    def ell(self):
        """Length of the partitioned job chain, more precisely l() function from the paper."""
        return let_we(self.fw[-1]) - let_re(self.bw[0])


def guenzel_23_equi_mda(chain: CEChain, Fi=None) -> float:
    """Compute MRT or MDA as in our paper using result X # TODO add definition/equation
    - optimized p for periodic synchrnous let tasks
    """
    # Construct F_i
    if Fi is None:
        Fi = find_fi(chain)

    # find analysis interval
    analysis_end = 2 * chain.hyperperiod() + chain.max_phase()

    # choose point for partitioning
    # for synchronous let just choose the task with highest period
    periods = [tsk.period for tsk in chain]
    part = periods.index(max(periods))

    # construct partitioned chains
    part_chains = []
    for number in itertools.count(start=Fi[part]):
        pc = PartitionedJobChain(part, chain, number)
        if let_re(pc.bw[0]) <= analysis_end:
            part_chains.append(pc)
        else:
            break

    assert all(pc.complete for pc in part_chains)
    return max([pc.ell() for pc in part_chains])


def guenzel_23_equi_mrt(chain: CEChain, Fi=None) -> float:
    return guenzel_23_equi_mda(chain, Fi)


def compute_mrrt(chain: CEChain, mrt: float = None) -> float:
    """Compute MRRT using the result from X # TODO add result
    Assumption: LET communication
    """
    if mrt is None:  # Compute MRT if not given
        mrt = our_mrt(chain)

    # difference between MRT and MRRT under LET is one period of the first task
    mrrt = mrt - chain[0].period

    return mrrt


def compute_mrda(chain: CEChain, mda: float = None) -> float:
    """Compute MRDA using the result from X # TODO add result
    Assumption: LET communication
    """
    if mda is None:  # Compute MRT if not given
        mda = our_mda(chain)

    # difference between MRT and MRRT under LET is one period of the last task
    mrda = mda - chain[-1].period

    return mrda

