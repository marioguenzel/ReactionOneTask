"""
Analysis from Hamann et al. 2017:
Communication Centric Design in Complex Automotive Embedded Systems.

- LET
- sporadic
"""

def hamann17(chain):
    latency = 0
    for task in chain:
        latency += task.max_iat + task.deadline
    return latency