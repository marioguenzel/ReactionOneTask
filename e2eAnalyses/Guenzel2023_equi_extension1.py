"""
Extension of the analysis from Guenzel et al.:
On the Equivalence of Maximum Reaction Time and Maximum Data Age for Cause-Effect Chains(2023)

The analysis is extended to implicit communication with the schedule, similar to:
Timing Analysis of Asynchronized Distributed Cause-Effect Chains (2021)
Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains (2023)

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
and https://github.com/tu-dortmund-ls12-rt/end-to-end
and https://github.com/tu-dortmund-ls12-rt/mrt_mda/

- implicit
- periodic
"""


import itertools
from cechains.chain import CEChain
from cechains.jobchain import PartitionedJobChain, abstr_to_jc
import utilities.analyzer_guenzel23 as analyzer


debug_flag = False  # flag to have breakpoint() when errors occur

#####
# Job chain constructions
#####

def get_fw_jobchain(ce_chain: CEChain, occurrence: int, ana):
    """Create (occurrence)-th immediate forward job chain. (under implicit comm.)"""

    abstr = []
    abstr.append(occurrence)  # first entry

    for task, next_task in zip(ce_chain[:-1], ce_chain[1:]):
        abstr.append(ana.find_next_fw(
            task, next_task, abstr[-1]))  # intermediate entries
        
    return abstr_to_jc(abstr, ce_chain)


def get_bw_jobchain(ce_chain: CEChain, occurrence: int, ana):
    """Create (occurrence)-th immediate backward job chain. (under implicit comm.)"""

    abstr = []
    abstr.append(occurrence)  # last entry

    for task, prev_task in zip(ce_chain[::-1][:-1], ce_chain[::-1][1:]):
        idx = ana.find_next_bw(
            task, prev_task, abstr[-1])
        abstr.append(idx)  # intermediate entries

        if idx == -1:  # check if incomplete
            break

    # Turn around the chain
    abstr = abstr[::-1]
        
    return abstr_to_jc(abstr, ce_chain)


def get_part_jobchain(part, chain, occurrence, ana):
    """Create a partitioned job chain.
    - part = where is the partioning
    - chain = cause-effect chain
    - occurrence = which chain
    - ana = analyzer for read/writes under implicit comm."""

    bw = get_bw_jobchain(CEChain(*chain[: part + 1], base_ts=chain.base_ts), occurrence, ana)
    fw = get_fw_jobchain(CEChain(*chain[part:], base_ts=chain.base_ts), occurrence + 1, ana)

    return PartitionedJobChain(chain, fw, bw)


def ell(pc : PartitionedJobChain, ana):
    """Length of the partitioned job chain, more precisely l() function from the paper."""
    return ana.wemax(pc.fw[-1].task, pc.fw[-1].occurrence) - ana.remin(pc.bw[0].task, pc.bw[0].occurrence)

#####
# Find Fi
#####

def find_fi(ce_chain: CEChain, ana) -> list[int]:
    """List of Fi values."""
    # one forward chain
    fc = get_fw_jobchain(ce_chain, 0, ana)
    F = fc[-1].occurrence
    # one backward chain
    bc = get_bw_jobchain(ce_chain, F, ana)
    Fi = [job.occurrence for job in bc]
    return Fi

#####
# New analysis, based on Guenzel2023_equi and Guenzel2023_inter
#####

def guenzel23_equi_impl_sched(chain):

    assert len(chain.base_ts.schedules.keys()) > 0
    schedules = chain.base_ts.schedules

    ana = analyzer.re_we_analyzer(schedules['bcet'], schedules['wcet'], chain.base_ts.hyperperiod())
    
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
    for occurrence in itertools.count(start=Fi[part]):
        pc = get_part_jobchain(part, chain, occurrence, ana)
        if ana.remin(pc.bw[0].task, pc.bw[0].occurrence) <= analysis_end:
            part_chains.append(pc)
        else:
            break

    assert all(pc.complete for pc in part_chains)
    return max([ell(pc, ana) for pc in part_chains])



