"""
Analysis from Kloda et al. 2018:
Latency analysis for data chains of real-time periodic tasks.

- implicit
- periodic

Implementation based on https://github.com/tu-dortmund-ls12-rt/end-to-end/blob/master/utilities/analyzer.py#L410
"""
import math
from cechains.chain import CEChain


def kloda18(chain):
    """Kloda analysis for the single ECU case with synchronous releases.

    Input: chain is one cause-effect chain. hyper_period is the hyperperiod
    of the underlying task set.
    """
    latency = 0
    for release_first_task_in_chain in range(0, max(1, chain.base_ts.hyperperiod()), chain[0].period):
        # Compute latency for a given first job.
        new_latency = kloda_rec(chain, release_first_task_in_chain, beginning=True)
        # Compare and store the results.
        latency = max(latency, new_latency)
    return latency


def kloda_rec(chain, rel_producer, beginning=True):
    """Recursive function to compute the reaction time by klodas analysis.

    Note: The additional period is already added with the beginning=True
    option.
    """
    wcrts = chain.base_ts.wcrts
    add = 0
    # Additional period at the beginning. (This is only done for the
    # initial case.)
    if beginning:
        add += chain[0].period

    producer_task = chain[0]  # producer

    # Final case
    if len(chain) == 1:
        return wcrts[producer_task] + add

    rem_chain = CEChain(*list(chain[1::]), base_ts=chain.base_ts)  # remaining chain
    consumer_task = rem_chain[0]  # consumer

    # Intermediate cases. Compute difference between producer and consumer.
    q = 0
    # Case: Producer has lower priority than consumer, i.e., the priority
    # value is higher. Note: We do not implement a processor change since
    # we consider only the single ECU case. (Kloda cannot be applied to
    # asynchronized ECUs.)
    if chain.base_ts.higher_prio(consumer_task, producer_task):
        q = wcrts[producer_task]
    rel_consumer = (math.ceil((rel_producer + q) / consumer_task.period) * consumer_task.period)
    return (add + rel_consumer - rel_producer + kloda_rec(rem_chain, rel_consumer, beginning=False))