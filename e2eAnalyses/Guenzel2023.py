import math
import itertools
from tasks.task import Task
from tasks.taskset import TaskSet
from cechains.chain import CEChain

# Sporadic + LET

def LET_spor(chain):
    """Upper bound for sporadic tasks under LET.
    - LET
    -sporadic
    """
    result = 0
    for tsk in chain:
        result += tsk.rel.maxiat + tsk.dl.dl
    return result


# Periodic + Implicit

def impl_per(chain):
    """Upper bound for periodic tasks under LET.
    - LET
    - periodic
    """
    # Compute chain hyperperiod and phase and maximum wcrt:
    hyper = chain.hyperperiod()
    max_phase = chain.max_phase()
    WCRT_max = max(chain.base_ts.wcrts[tsk] for tsk in chain)

    lengths = []

    for mvar in itertools.count(start=1):
        # Principle 1 and chain definition
        zvar = _release(mvar, chain[0])
        relvar = _release(mvar + 1, chain[0])

        # check conditions
        if relvar + chain.base_ts.wcrts[chain[0]] < max_phase:
            continue
        if zvar > max_phase + hyper + WCRT_max:
            break

        for this_tsk, next_tsk in zip(chain[:-1], chain[1:]):
            # Principle 2 (Compute release of next job in the job chain)
            if chain.base_ts.higher_prio(this_tsk, next_tsk):
                compare_value = relvar
            else:
                compare_value = relvar + chain.base_ts.wcrts[this_tsk]
            relvar = _release_after(compare_value, next_tsk)

        # Principle 3
        zprimevar = relvar + chain.base_ts.wcrts[chain[-1]]

        lengths.append(zprimevar - zvar)

    return max(lengths)


# Periodic + LET

def LET_per(chain):
    """Upper bound for periodic tasks under LET.
    - LET
    - periodic
    """
    # Compute chain hyperperiod and phase:
    hyper = chain.hyperperiod()
    max_phase = chain.max_phase()
    WCRT_max = max(chain.base_ts.wcrts[tsk] for tsk in chain)

    lengths = []

    for mvar in itertools.count(start=1):
        # Principle 1 and chain definition
        zvar = _release(mvar, chain[0])
        relvar = _release(mvar + 1, chain[0])

        # check conditions
        if relvar + chain.base_ts.wcrts[chain[0]] < max_phase:
            continue
        if zvar > max_phase + hyper + WCRT_max:
            break

        for this_tsk, next_tsk in zip(chain[:-1], chain[1:]):
            # Principle 2 (Compute release of next job in the job chain)
            compare_value = relvar + this_tsk.dl.dl
            relvar = _release_after(compare_value, next_tsk)

        # Principle 3
        zprimevar = relvar + chain[-1].dl.dl

        lengths.append(zprimevar - zvar)

    return max(lengths)



#####
# Help functions
#####

def _release_after(time, tsk):
    """Next release of tsk at or after 'time' for periodic tasks."""
    return tsk.rel.phase + math.ceil((time - tsk.rel.phase) / tsk.rel.period) * tsk.rel.period


def _release(m, tsk):
    """Time of the m-th job release of a periodic task.
    (First job is at m=1.)"""
    return tsk.rel.phase + (m - 1) * tsk.rel.period