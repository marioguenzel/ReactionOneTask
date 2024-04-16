"""Analysis from Hamann et al. 2017:
Communication Centric Design in Complex Automotive Embedded Systems.
- LET
- sporadic
"""

def hamann17(chain):
    result = 0
    for tsk in chain:
        result += tsk.rel.maxiat + tsk.dl.dl
    return result