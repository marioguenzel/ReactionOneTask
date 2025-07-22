import itertools
import random
from benchmarks.benchmark_Uniform import gen_taskset
from cechains.chain import CEChain
from e2eAnalyses.Guenzel2023_inter import guenzel23_local_mrt
from framework import adjust_taskset_bcets, remove_invalid_tasksets
from tasks.taskset import TaskSet
from utilities.scheduler import schedule_task_set

automotive_periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000]
min_auto_periods = 1
max_auto_periods = 2000

for idx in itertools.count():
    if idx % 1000 == 0:
        print(f"RUN {idx}")
    # Generate cause-effect chains with typical parameters
    taskset = gen_taskset(0.1,3,3,min_auto_periods,max_auto_periods,automotive_periods,random.randint(0, 2**32 - 1))
    # taskset = gen_taskset(0.5,random.randint(0, 2**32 - 1))

    # CE Chains
    ce_chains = [CEChain(taskset[i], base_ts=taskset) for i in range(len(taskset))]

    # === Typical order ===
    # Schedule
    taskset.compute_wcrts()
    if len(remove_invalid_tasksets([taskset])) == 0:
        # print("Removed1")
        continue

    taskset.schedules = schedule_task_set(ce_chains, taskset)[1]

    res_before = []
    for ce in ce_chains:
        res_before.append(guenzel23_local_mrt(ce))

    
    # === Other order ===
    taskset_after = TaskSet(taskset[0],taskset[2],taskset[1])
    ce_chains_after = [CEChain(taskset_after[i], base_ts=taskset_after) for i in range(len(taskset_after))]

    # Schedule
    taskset_after.compute_wcrts()
    if len(remove_invalid_tasksets([taskset_after])) == 0:
        # print("Removed2")
        continue
    
    taskset_after.schedules = schedule_task_set(ce_chains_after, taskset_after)[1]

    res_after = []
    for ce in ce_chains_after:
        res_after.append(guenzel23_local_mrt(ce))

    # print(res_before, res_after)

    if res_before[1]-0.000001> res_after[2] or res_before[2]<res_after[1]-0.000001:
        breakpoint()

print("Reached limit")
    
# for taskset in tasksets:
#         adjust_taskset_bcets(taskset, 1.0)
#         taskset.rate_monotonic_scheduling()
#         taskset.compute_wcrts()

# tasksets = remove_invalid_tasksets(tasksets)

