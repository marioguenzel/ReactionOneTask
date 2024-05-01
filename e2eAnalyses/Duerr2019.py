"""
Analyses from Duerr et al. 2019, CASES:
End-to-end timing analysis of sporadic cause-effect chains in distributed systems.

- implicit
- sporadic

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end/blob/master/utilities/analyzer.py#L368
"""

def duerr19(chain):
    wcrts = chain.base_ts.wcrts
    latency = 0
    for idx in range(len(chain)):
        if idx == len(chain) - 1 or chain.base_ts.higher_prio(chain[idx + 1], chain[idx]):
            latency += chain[idx].max_iat + wcrts[chain[idx]]
        else:
            latency += chain[idx].max_iat + max(wcrts[chain[idx]] - chain[idx + 1].max_iat, 0)
    return latency


def duerr_19_mrt(chain):
    """Maximum reaction time analysis from Duerr (Theorem 5.4)"""
    wcrts = chain.base_ts.wcrts
    
    # Compute latency.
    latency = chain[0].max_iat + wcrts[chain[-1]]
    for task, next_task in zip(chain[:-1], chain[1:]):
        if (chain.base_ts.higher_prio(next_task, task)
                or next_task.inter_ecu_communication or task.inter_ecu_communication):
            part2 = wcrts[task]
        else:
            part2 = 0
        latency += max(wcrts[task], next_task.max_iat + part2)

    return latency


def duerr_19_mrda(chain):
    """Maximum data age analysis from Duerr (Theorem 5.10)"""
    wcrts = chain.base_ts.wcrts

    # Compute latency.
    latency = wcrts[chain[-1]]
    for task, next_task in zip(chain[:-1], chain[1:]):
        if (chain.base_ts.higher_prio(next_task, task)
                or next_task.inter_ecu_communication or task.inter_ecu_communication):
            part2 = wcrts[task]
        else:
            part2 = 0
        latency += task.max_iat + part2

    return latency