"""
Analyses from Guenzel et al.:
Timing Analysis of Asynchronized Distributed Cause-Effect Chains (2021)
Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains (2023)

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
and https://github.com/tu-dortmund-ls12-rt/end-to-end
"""


import math
import itertools
from tasks.taskset import TaskSet
from cechains.chain import CEChain
from cechains.jobchain import PartitionedJobChain, abstr_to_jc
import utilities.event_simulator as es
from e2eAnalyses.Davare2007 import davare07


debug_flag = False  # flag to have breakpoint() when errors occur

#####
# Helper functions
#####

def find_next_fw(curr_task, nxt_task, curr_index, base_ts):
    wemax = curr_task.period * curr_index + base_ts.wcrts[curr_task]     # approximated wemax with wcrt

    idx = math.floor(wemax / nxt_task.period)
    while nxt_task.period * idx < wemax:
        idx +=1

    return idx


def find_next_bw(curr_task, prev_task, curr_index, base_ts):
    remin = curr_task.period * curr_index   # approximated remin with release time of job

    idx = math.ceil(remin / prev_task.period)
    while prev_task.period * idx + base_ts.wcrts[prev_task] > remin:
        idx -=1

    return idx


#####
# Job chain constructions
#####

def get_fw_jobchain(ce_chain: CEChain, occurrence: int):
    """Create (occurrence)-th immediate forward job chain. (under implicit comm.)"""

    abstr = []
    abstr.append(occurrence)  # first entry

    for task, next_task in zip(ce_chain[:-1], ce_chain[1:]):
        idx = find_next_fw(task, next_task, abstr[-1], ce_chain.base_ts)  # intermediate entries
        abstr.append(idx)
        
    return abstr_to_jc(abstr, ce_chain)


def get_bw_jobchain(ce_chain: CEChain, occurrence: int):
    """Create (occurrence)-th immediate backward job chain. (under implicit comm.)"""

    abstr = []
    abstr.append(occurrence)  # last entry

    for task, prev_task in zip(ce_chain[::-1][:-1], ce_chain[::-1][1:]):
        idx = find_next_bw(task, prev_task, abstr[-1], ce_chain.base_ts)
        abstr.append(idx)  # intermediate entries

        if idx < 0:  # check if incomplete
            break

    # Turn around the chain
    abstr = abstr[::-1]
        
    return abstr_to_jc(abstr, ce_chain)


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
    return (pc.fw[-1].task.period * pc.fw[-1].occurrence + pc.base_ce_chain.base_ts.wcrts[pc.fw[-1].task]) - (pc.bw[0].task.period * pc.bw[0].occurrence)


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
# New analysis, based on Guenzel2023_equi and Guenzel2023_inter
#####

def our_mrt_mRda_lst(chain, bcet, wcet):
    
    # Construct F_i
    Fi = find_fi(chain)

    # find analysis interval
    analysis_end = 2 * chain.base_ts.hyperperiod() + chain.base_ts.max_phase()

    # choose point for partitioning
    # just choose the task with highest period
    periods = [tsk.period for tsk in chain]
    part = periods.index(max(periods))

    # construct partitioned chains
    part_chains = []
    for occurrence in itertools.count(start=Fi[part]):
        pc = get_part_jobchain(part, chain, occurrence)
        if pc.bw[0].task.period * pc.bw[0].occurrence <= analysis_end:
            part_chains.append(pc)
        else:
            break

    assert all(pc.complete for pc in part_chains)
    return max([ell(pc) for pc in part_chains], default=0) #   TODO fixme


def newAna2(chain):
    latency = our_mrt_mRda_lst(chain, 1.0, 1.0)
    return latency



