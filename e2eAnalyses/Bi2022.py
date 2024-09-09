"""
Analysis from Bi et al. 2022:
Efficient Maximum Data Age Analysis for Cause-Effect Chains in Automotive Systems.

Implementation was provided directly by the authors and adjusted to fit the system model.

- implicit
- periodic
"""


import math


def bi22(chain):
    """
    Ren's maximum data age analysis for the single ECU case.

    Input: chain is one cause-effect chain.
    """
    wcrts = chain.base_ts.wcrts
    n = chain.length()
    if(n == 1):
        MDA = wcrts[chain[0]]
    else:
        MDA = wcrts[chain[-1]]
        for i in range(n-1):
            producer = chain[i]
            consumer = chain[i+1]
            eta = math.gcd(producer.period, consumer.period)
            if producer.priority < consumer.priority:
                MDA = MDA + producer.period - eta
            elif wcrts[producer] % eta == 0:
                MDA = MDA + wcrts[producer] + producer.period - eta
            else:
                MDA = MDA + wcrts[producer] + producer.period - wcrts[producer] % eta
    # Store result.
    #chain.DBAge = MDA
    return MDA

def bi22_inter(*local_chains):
    """
    Ren's maximum data age analysis for interconnected cause-effect chains.

    Input: local_chains is a list of cause-effect chains.
    """
    inter_chain = list(local_chains)
    inter_MDA = 0  # total data age
    for local_chain in inter_chain:
        inter_MDA += bi22(local_chain)

    return inter_MDA

# --------------------------------------------------------------------------- #