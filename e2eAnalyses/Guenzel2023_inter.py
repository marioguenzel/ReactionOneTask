"""
Analyses from Guenzel et al.:
Timing Analysis of Asynchronized Distributed Cause-Effect Chains (2021)
Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains (2023)

Basis from: https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
and https://github.com/tu-dortmund-ls12-rt/end-to-end
"""

import utilities.analyzer_guenzel23 as analyzer


# single ecu
def guenzel23_local_mrt(chain):
    assert len(chain.base_ts.schedules.keys()) > 0
    schedules = chain.base_ts.schedules

    mrt = analyzer.max_reac_local(
        chain, 
        chain.base_ts, 
        schedules['wcet'], 
        schedules['bcet']
    )

    return mrt


def guenzel23_local_mda(chain):
    assert len(chain.base_ts.schedules.keys()) > 0
    schedules = chain.base_ts.schedules

    mda, mrda = analyzer.max_age_local(
        chain, 
        chain.base_ts,
        schedules['wcet'], 
        schedules['bcet']
    )

    return mda


def guenzel23_local_mrda(chain):
    assert len(chain.base_ts.schedules.keys()) > 0
    schedules = chain.base_ts.schedules

    mda, mrda = analyzer.max_age_local(
        chain, 
        chain.base_ts,
        schedules['wcet'], 
        schedules['bcet']
    )

    return mrda


# inter ecu analyses
def guenzel23_inter_mrt(*local_chains):
    inter_chain = list(local_chains)
    latency = 0
    for local_chain in inter_chain:
        latency+=guenzel23_local_mrt(local_chain)
    return latency


def guenzel23_inter_mrda(*local_chains):
    inter_chain = list(local_chains)
    latency = 0
    for local_chain in inter_chain:
        latency+=guenzel23_local_mrda(local_chain)
    return latency
