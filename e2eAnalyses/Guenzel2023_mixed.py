"""
Analyses from Guenzel et al., 2023:
Timing Analysis of Cause-Effect Chains with Heterogeneous Communication Mechanisms

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed
"""


import math
import itertools
from tasks.task import Task
from tasks.taskset import TaskSet
from cechains.chain import CEChain
from e2eAnalyses.Duerr2019 import duerr_19_mrt

# Sporadic + LET

def LET_spor(chain):
    """Upper bound for sporadic tasks under LET.
    - LET
    -sporadic
    """
    result = 0
    for task in chain:
        result += task.max_iat + task.deadline
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
    WCRT_max = max(chain.base_ts.wcrts[task] for task in chain)

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

        for this_task, next_task in zip(chain[:-1], chain[1:]):
            # Principle 2 (Compute release of next job in the job chain)
            if chain.base_ts.higher_prio(this_task, next_task):
                compare_value = relvar
            else:
                compare_value = relvar + chain.base_ts.wcrts[this_task]
            relvar = _release_after(compare_value, next_task)

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
    WCRT_max = max(chain.base_ts.wcrts[task] for task in chain)

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

        for this_task, next_task in zip(chain[:-1], chain[1:]):
            # Principle 2 (Compute release of next job in the job chain)
            compare_value = relvar + this_task.deadline
            relvar = _release_after(compare_value, next_task)

        # Principle 3
        zprimevar = relvar + chain[-1].deadline

        lengths.append(zprimevar - zvar)

    return max(lengths)



#####
# Mixed
#####

def guenzel_23_mix_pessimistic(chain):
    """Pessimistic Analysis for mixed chains."""
    result = 0
    for task in chain:
        if task.communication_policy == 'implicit':
            result += task.max_iat + chain.base_ts.wcrts[task]
        elif task.communication_policy == 'LET':
            result += task.max_iat + task.deadline
        else:
            raise ValueError(f"{task.communication_policy=} cannot be handled by the analysis.")

    return result


def guenzel_23_mix(
        chain,
        impl_spor=duerr_19_mrt,
        impl_per=impl_per,
        let_spor=LET_spor,
        let_per=LET_per
):
    """Our analysis. Cut to make homogeneous, then apply analyses."""
    cutted_chains = _cut_chain(chain, communication=True, release=True)
    result = 0
    for ch in cutted_chains:
        if ch.check_feature('communication_policy') == 'implicit' and ch.check_feature('release_pattern') == 'sporadic':
            result += impl_spor(ch)
        elif ch.check_feature('communication_policy') == 'implicit' and ch.check_feature('release_pattern') == 'periodic':
            result += impl_per(ch)
        elif ch.check_feature('communication_policy') == 'LET' and ch.check_feature('release_pattern') == 'sporadic':
            result += let_spor(ch)
        elif ch.check_feature('communication_policy') == 'LET' and ch.check_feature('release_pattern') == 'periodic':
            result += let_per(ch)
        else:
            raise ValueError(
                f"{ch.check_feature('communication_policy')=} and {ch.check_feature('release_pattern')=} cannot be handled by the analysis.")

    return result


def _cut_chain(chain, communication=True, release=True):
    """Cut cause-effect chain into homogeneous chains."""
    new_chains = []

    for idx, task in enumerate(chain):
        if (
                idx == 0 or
                (communication and task.communication_policy != curr_comm) or
                (release and task.release_pattern != curr_rel)
        ):
            curr_comm = task.communication_policy
            curr_rel = task.release_pattern
            new_chains.append(CEChain(task, base_ts=chain.base_ts))
        else:
            new_chains[-1].append(task)
    return new_chains


def guenzel_23_mix_improved(chain):
    """Our analysis. Cut only when release constraint changes."""
    cutted_chains = _cut_chain(chain, communication=False, release=True)

    result = 0
    for ch in cutted_chains:
        if ch.check_feature('release_pattern') == 'sporadic':
            result += mix_sporadic(ch)
        elif ch.check_feature('release_pattern') == 'periodic':
            result += mix_periodic(ch)
        else:
            raise ValueError(f"{ch.check_feature('release_pattern')=} cannot be handled by the analysis.")
    return result


def mix_sporadic(chain):
    """Analysis for sporadic tasks and mixed communication means."""
    assert all([task.communication_policy in ['LET', 'implicit'] for task in chain])
    result = 0
    for idx in range(len(chain)):
        result += chain[idx].max_iat + _CX(idx, chain)
    return result


def _CX(idx, chain):
    """CX from our work."""
    if chain[idx].communication_policy == 'LET':
        return chain[idx].deadline
    elif (idx != len(chain) - 1 and
          chain[idx + 1].communication_policy == 'implicit' and
          chain.base_ts.higher_prio(chain[idx], chain[idx + 1])):
        return max(chain.base_ts.wcrts[chain[idx]] - chain[idx + 1].max_iat, 0)
    else:
        return chain.base_ts.wcrts[chain[idx]]


def mix_periodic(chain):
    """Analysis for periodic tasks and mixed communication means."""
    # Compute chain hyperperiod and phase:
    hyper = chain.hyperperiod()
    max_phase = chain.max_phase()
    WCRT_max = max(chain.base_ts.wcrts[task] for task in chain)

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

        for idx, (this_task, next_task) in enumerate(zip(chain[:-1], chain[1:])):
            # Principle 2 (Compute release of next job in the job chain)
            compare_value = relvar + _add_to_compare_value_from_table(idx, chain)
            relvar = _release_after(compare_value, next_task)

        # Principle 3
        if chain[-1].communication_policy == 'LET':
            zprimevar = relvar + chain[-1].deadline
        elif chain[-1].communication_policy == 'implicit':
            zprimevar = relvar + chain.base_ts.wcrts[chain[-1]]

        lengths.append(zprimevar - zvar)

    return max(lengths)


def _add_to_compare_value_from_table(idx, chain):
    """The compare value used in the periodic analysis to find the next job.
    Please note: idx in range {0,1, ... , len(chain)-2}"""
    this_task = chain[idx]
    next_task = chain[idx + 1]

    if this_task.communication_policy == 'LET':
        return this_task.deadline
    elif this_task.communication_policy == 'implicit' and next_task.communication_policy == 'LET':
        return chain.base_ts.wcrts[this_task]
    elif this_task.communication_policy == 'implicit' and next_task.communication_policy == 'implicit':
        if chain.base_ts.higher_prio(this_task, next_task):
            return 0
        else:
            return chain.base_ts.wcrts[this_task]
    else:
        raise ValueError(f"{this_task.communication_policy=} and {next_task.communication_policy=} cannot be handled by the analysis.")


#####
# Help functions
#####

def _release_after(time, task):
    """Next release of task at or after 'time' for periodic tasks."""
    return task.phase + math.ceil((time - task.phase) / task.period) * task.period


def _release(m, task):
    """Time of the m-th job release of a periodic task.
    (First job is at m=1.)"""
    return task.phase + (m - 1) * task.period
