def davare(chain):
    """Analysis from Davare et al. 2007, DAC:
    Period optimization for hard real-time distributed automotive systems.
    - implicit
    - sporadic
    """
    wcrts = chain.base_ts.wcrts
    result = 0
    for tsk in chain:
        result += tsk.rel.maxiat + wcrts[tsk]
    return result
