"""
Analyses from Duerr et al. 2019, CASES:
End-to-end timing analysis of sporadic cause-effect chains in distributed systems.

- implicit
- sporadic

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end/blob/master/utilities/analyzer.py#L368
"""

import itertools

def duerr19(chain):
    wcrts = chain.base_ts.wcrts
    latency = 0
    for idx in range(len(chain)):
        if idx == len(chain) - 1 or chain.base_ts.higher_prio(chain[idx + 1], chain[idx]):
            latency += chain[idx].max_iat + wcrts[chain[idx]]
        else:
            latency += chain[idx].max_iat + max(wcrts[chain[idx]] - chain[idx + 1].max_iat, 0)
    return latency


def duerr19_mrt(*local_chains):
    """Maximum reaction time analysis from Duerr (Theorem 5.4)"""
    inter_chain = list(local_chains)
    wcrts = get_all_wcrts(inter_chain)
    tasks = list(itertools.chain(*[local_chain.lst for local_chain in inter_chain]))
    
    # Compute latency.
    latency = tasks[0].max_iat + wcrts[tasks[-1]]
    for task, next_task in zip(tasks[:-1], tasks[1:]):
        ecu1 = get_ecu(inter_chain, task)
        ecu2 = get_ecu(inter_chain, next_task)
        if ecu1 != ecu2 or inter_chain[ecu1].base_ts.higher_prio(next_task, task):
            part2 = wcrts[task]
        else:
            part2 = 0
        latency += max(wcrts[task], next_task.max_iat + part2)

    return latency


def duerr19_mrda(*local_chains):
    """Maximum data age analysis from Duerr (Theorem 5.10)"""
    inter_chain = list(local_chains)
    wcrts = get_all_wcrts(inter_chain)
    tasks = list(itertools.chain(*[local_chain.lst for local_chain in inter_chain]))

    # Compute latency.
    latency = wcrts[tasks[-1]]
    for task, next_task in zip(tasks[:-1], tasks[1:]):
        ecu1 = get_ecu(inter_chain, task)
        ecu2 = get_ecu(inter_chain, next_task)
        if ecu1 != ecu2 or inter_chain[ecu1].base_ts.higher_prio(next_task, task):
            part2 = wcrts[task]
        else:
            part2 = 0
        latency += task.max_iat + part2

    return latency


# helper functions

def get_all_wcrts(inter_chain):
    wcrts = dict()
    for local_chain in inter_chain:
        wcrts = wcrts | local_chain.base_ts.wcrts
    return wcrts


def get_ecu(inter_chain, task):
    for i in range(len(inter_chain)):
        if inter_chain[i].contains(task):
            return i
    return -1