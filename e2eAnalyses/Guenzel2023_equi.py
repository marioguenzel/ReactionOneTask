"""Analysis applied in the evaluation.
Assumptions:
- LET
- periodic"""
import itertools
import math
from cechains.chain import CEChain
from cechains.jobchain import JobChain, PartitionedJobChain
from tasks.task import Task
from tasks.job import Job


#####
# Help functions for LET communication
#####


def let_we(job: Job):
    """Write-event of job under LET."""
    return job.task.phase + job.task.period * job.occurrence + job.task.deadline


def let_re(job: Job):
    """Read-event of job under LET."""
    return job.task.phase + job.task.period * job.occurrence


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
# Job chain constructions
#####

def get_fw_jobchain(ce_chain: CEChain, occurrence: int):
    """Create (occurrence)-th immediate forward job chain. (under implicit comm.)"""

    # first job
    job_lst = [Job(ce_chain[0], occurrence)]

    # next jobs
    for tsk in ce_chain[1:]:
        # find next job
        next_job_occurrence = let_re_geq(let_we(job_lst[-1]), tsk)

        # add job to chain
        job_lst.append(Job(tsk, next_job_occurrence))
        
    return JobChain(*job_lst)


def get_bw_jobchain(ce_chain: CEChain, occurrence: int):
    """Create (occurrence)-th immediate backward job chain. (under implicit comm.)"""

    # last job
    job_lst = [Job(ce_chain[-1], occurrence)]

    # previous jobs jobs
    for tsk in ce_chain[0:-1][::-1]:  # backwards except the last
        # find previous job
        previous_job_occurrence = let_we_leq(let_re(job_lst[0]), tsk)

        # add job to chain
        job_lst.insert(0, Job(tsk, previous_job_occurrence))
    
    return JobChain(*job_lst)


def get_part_jobchain(part, chain, occurrence):
    """Create a partitioned job chain.
    - part = where is the partioning
    - chain = cause-effect chain
    - occurrence = which chain
    - ana = analyzer for read/writes under implicit comm."""

    bw = get_bw_jobchain(CEChain(*chain[: part + 1], base_ts=chain.base_ts), occurrence)
    fw = get_fw_jobchain(CEChain(*chain[part:], base_ts=chain.base_ts), occurrence + 1)

    return PartitionedJobChain(chain, fw, bw)


def ell(pc : PartitionedJobChain):
    """Length of the partitioned job chain, more precisely l() function from the paper."""
    return let_we(pc.fw[-1]) - let_re(pc.bw[0])


#####
# Find Fi
#####

def find_fi(ce_chain: CEChain) -> list[int]:
    """List of Fi values."""
    # one forward chain
    fc = get_fw_jobchain(ce_chain, 0)
    F = fc[-1].occurrence
    # one backward chain
    bc = get_bw_jobchain(ce_chain, F)

    Fi = [job.occurrence for job in bc]
    return Fi


#####
# guenzel_23_equi analysis
#####


def guenzel23_equi_mda(chain: CEChain, Fi=None) -> float:
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
    for occurrence in itertools.count(start=Fi[part]):
        pc = get_part_jobchain(part, chain, occurrence)
        if let_re(pc.bw[0]) <= analysis_end:
            part_chains.append(pc)
        else:
            break

    assert all(pc.complete for pc in part_chains)
    return max([ell(pc) for pc in part_chains])


def guenzel23_equi_mrt(chain: CEChain, Fi=None) -> float:
    return guenzel23_equi_mda(chain, Fi)


def guenzel23_equi_mrrt(chain: CEChain, mrt: float = None) -> float:
    """Compute MRRT using the result from X # TODO add result
    Assumption: LET communication
    """
    if mrt is None:  # Compute MRT if not given
        mrt = guenzel23_equi_mrt(chain)

    # difference between MRT and MRRT under LET is one period of the first task
    mrrt = mrt - chain[0].period

    return mrrt


def guenzel23_equi_mrda(chain: CEChain, mda: float = None) -> float:
    """Compute MRDA using the result from X # TODO add result
    Assumption: LET communication
    """
    if mda is None:  # Compute MRT if not given
        mda = guenzel23_equi_mda(chain)

    # difference between MRT and MRRT under LET is one period of the last task
    mrda = mda - chain[-1].period

    return mrda

