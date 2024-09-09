"""
Analysis from Davare et al. 2007, DAC:
Period optimization for hard real-time distributed automotive systems.

- implicit
- sporadic
"""


def davare07(chain):
    wcrts = chain.base_ts.wcrts
    latency = 0
    for task in chain:
        latency += task.max_iat + wcrts[task]
    return latency


def davare07_inter(*local_chains):
    inter_chain = list(local_chains)
    latency = 0
    for local_chain in inter_chain:
        latency += davare07(local_chain)
    return latency
