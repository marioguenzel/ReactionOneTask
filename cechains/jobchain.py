import math

from tasks.task import Task
from tasks.job import Job
from cechains.chain import CEChain

#####
# Help functions for LET communication
#####

def let_we(job: Job):
    """Write-event of job under LET."""
    return job.task.rel.phase + job.task.rel.period * job.number + job.task.dl.dl


def let_re(job: Job):
    """Read-event of job under LET."""
    return job.task.rel.phase + job.task.rel.period * job.number


def let_re_geq(time, task: Task):
    """Number of earliest job with read-event of (task) at or after (time)."""
    return max(math.ceil((time - task.rel.phase) / task.rel.period), 0)


def let_re_gt(time, task: Task):
    """Number of earliest job with read-event of (task) after (time)."""
    return max(math.floor((time - task.rel.phase) / task.rel.period) + 1, 0)


def let_we_leq(time, task: Task):
    """Number of latest job with write-event of (task) at or before (time)."""
    return math.floor((time - task.rel.phase - task.dl.dl) / task.rel.period)


#####
# Help functions for implicit communication
#####

def impl_we(job: Job, schedule: dict):
    """Write-event of job under implicit communication."""
    return job.task.rel.phase + job.task.rel.period * job.number + job.task.dl.dl


def impl_re(job: Job, schedule: dict):
    """Read-event of job under implicit communication."""
    return job.task.rel.phase + job.task.rel.period * job.number


def impl_re_geq(time, task: Task, schedule: dict):
    """Number of earliest job with read-event of (task) at or after (time)."""
    return max(math.ceil((time - task.rel.phase) / task.rel.period), 0)


def impl_re_gt(time, task: Task, schedule: dict):
    """Number of earliest job with read-event of (task) after (time)."""
    return max(math.floor((time - task.rel.phase) / task.rel.period) + 1, 0)


def impl_we_leq(time, task: Task, schedule: dict):
    """Number of latest job with write-event of (task) at or before (time)."""
    return math.floor((time - task.rel.phase - task.dl.dl) / task.rel.period)

#####
# Help functions
#####

def we(job: Job):
    """Write-event of job"""
    if job.task.communication_policy == 'implicit':
        #TODO
        ...
    elif job.task.communication_policy == 'LET':
        return let_we(job)


def re(job: Job):
    """Read-event of job under LET."""
    if job.task.communication_policy == 'implicit':
        #TODO
        ...
    elif job.task.communication_policy == 'LET':
        return let_re(job)


def re_geq(time, task: Task):
    """Number of earliest job with read-event of (task) at or after (time)."""
    if task.communication_policy == 'implicit':
        #TODO
        ...
    elif task.communication_policy == 'LET':
        return let_re_geq(time, task)


def re_gt(time, task: Task):
    """Number of earliest job with read-event of (task) after (time)."""
    if task.communication_policy == 'implicit':
        #TODO
        ...
    elif task.communication_policy == 'LET':
        return let_re(time, task)


def we_leq(time, task: Task):
    """Number of latest job with write-event of (task) at or before (time)."""
    if task.communication_policy == 'implicit':
        #TODO
        ...
    elif task.communication_policy == 'LET':
        return let_re(time, task)


#####
# Job chain definitions
#####

class JobChain(list):

    def __init__(self, *jobs):
        super().__init__(jobs)

    def __str__(self, no_braces=False):
        return "[ " + " -> ".join([str(j) for j in self]) + " ]"


class ForwardJobChain(JobChain):
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


class BackwardJobChain:

    def __init__(self) -> None:
        pass


class AugmentedForwardJobChain:

    def __init__(self) -> None:
        pass


class AugmentedBackwardJobChain:

    def __init__(self) -> None:
        pass