"""Analysis from Duerr et al. 2019, CASES:
End-to-end timing analysis of sporadic cause-effect chains in distributed systems.
- implicit
- sporadic
"""

def duerr19(chain):
    wcrts = chain.base_ts.wcrts
    result = 0
    for idx in range(len(chain)):
        if idx == len(chain) - 1 or chain.base_ts.higher_prio(chain[idx + 1], chain[idx]):
            result += chain[idx].rel.maxiat + wcrts[chain[idx]]
        else:
            result += chain[idx].rel.maxiat + max(wcrts[chain[idx]] - chain[idx + 1].rel.maxiat, 0)
    return result