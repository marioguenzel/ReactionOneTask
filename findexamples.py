import itertools
import random
from benchmarks.benchmark_Uniform import gen_taskset
from cechains.chain import CEChain
from e2eAnalyses.Guenzel2023_inter import guenzel23_local_mrt
from framework import adjust_taskset_bcets, remove_invalid_tasksets
from tasks.task import Task
from tasks.taskset import TaskSet
from utilities.scheduler import schedule_task_set


# Automated Search
def search():
    '''Swap the bottom two tasks.'''
    automotive_periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000]
    min_auto_periods = 1
    max_auto_periods = 2000

    periods = list(range(1,11))
    min_periods = 1
    max_periods = 11

    removed = 0

    for idx in itertools.count():
        if idx % 1000 == 0:
            print(f"RUN {idx}:: Removed: {removed}, Included: {idx-removed}")
        # Generate cause-effect chains with typical parameters
        taskset = gen_taskset(0.4,4,4,min_periods,max_periods,periods,random.randint(0, 2**32 - 1))
        # taskset = gen_taskset(0.5,random.randint(0, 2**32 - 1))

        sorted_tasklist = [tsk for tsk in taskset]
        sorted_tasklist.sort(key=lambda t: t.period)
        taskset = TaskSet(*sorted_tasklist)

        # Find with different periods
        if taskset[-1].period == taskset[-2].period:
            removed +=1
            continue
        # if not all(taskset[i].period < taskset[i+1].period for i in range(len(taskset)-1)):
        #     removed +=1
        #     continue

        # CE Chains
        ce_chains = [CEChain(taskset[i], base_ts=taskset) for i in range(len(taskset))]

        # === Typical order ===
        # Schedule
        taskset.compute_wcrts()
        if len(remove_invalid_tasksets([taskset])) == 0:
            removed += 1
            continue

        taskset.schedules = schedule_task_set(ce_chains, taskset)[1]

        res_before = []
        for ce in ce_chains:
            res_before.append(guenzel23_local_mrt(ce))

        
        # === Other order ===
        tsk_lst = [tsk for tsk in taskset]
        tsk_lst[-1], tsk_lst[-2] = tsk_lst[-2], tsk_lst[-1]
        taskset_after = TaskSet(*tsk_lst)
        ce_chains_after = [CEChain(taskset_after[i], base_ts=taskset_after) for i in range(len(taskset_after))]

        # Schedule
        taskset_after.compute_wcrts()
        if len(remove_invalid_tasksets([taskset_after])) == 0:
            removed +=1
            continue
        
        taskset_after.schedules = schedule_task_set(ce_chains_after, taskset_after)[1]

        res_after = []
        for ce in ce_chains_after:
            res_after.append(guenzel23_local_mrt(ce))

        # print(res_before, res_after)

        # if res_before[1]> res_after[2] or res_before[2]<res_after[1]:
        #     print(res_before, res_after)

        # if res_before[-2]-0.000001> res_after[-1] or res_before[-1]<res_after[-2]-0.000001:
        # if res_before[-2]-0.000001> res_after[-1]:
        if res_before[-2]+0.000001 >= res_after[-1] and res_before[-1]-0.000001 > res_after[-2]:
            taskset.print_tasks()
            print(res_before, res_after)
            breakpoint()

def search2():
    '''Swap the medium two tasks (From DM to not DM) and check whether that improves the latency of the last task.'''
    automotive_periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000]
    min_auto_periods = 1
    max_auto_periods = 2000

    periods = list(range(1,11))
    min_periods = 1
    max_periods = 11

    removed = 0

    for idx in itertools.count():
        if idx % 1000 == 0:
            print(f"RUN {idx}:: Removed: {removed}, Included: {idx-removed}")
        # Generate cause-effect chains with typical parameters
        taskset = gen_taskset(0.4,4,4,min_periods,max_periods,periods,random.randint(0, 2**32 - 1))
        # taskset = gen_taskset(0.5,random.randint(0, 2**32 - 1))

        sorted_tasklist = [tsk for tsk in taskset]
        sorted_tasklist.sort(key=lambda t: t.period)
        taskset = TaskSet(*sorted_tasklist)

        # Find with different periods
        if taskset[-2].period == taskset[-3].period:
            removed +=1
            continue
        # if not all(taskset[i].period < taskset[i+1].period for i in range(len(taskset)-1)):
        #     removed +=1
        #     continue

        # CE Chains
        ce_chains = [CEChain(taskset[i], base_ts=taskset) for i in range(len(taskset))]

        # === Typical order ===
        # Schedule
        taskset.compute_wcrts()
        if len(remove_invalid_tasksets([taskset])) == 0:
            removed += 1
            continue

        taskset.schedules = schedule_task_set(ce_chains, taskset)[1]

        res_before = []
        for ce in ce_chains:
            res_before.append(guenzel23_local_mrt(ce))

        
        # === Other order ===
        tsk_lst = [tsk for tsk in taskset]
        tsk_lst[-3], tsk_lst[-2] = tsk_lst[-2], tsk_lst[-3]
        taskset_after = TaskSet(*tsk_lst)
        ce_chains_after = [CEChain(taskset_after[i], base_ts=taskset_after) for i in range(len(taskset_after))]

        # Schedule
        taskset_after.compute_wcrts()
        if len(remove_invalid_tasksets([taskset_after])) == 0:
            removed +=1
            continue
        
        taskset_after.schedules = schedule_task_set(ce_chains_after, taskset_after)[1]

        res_after = []
        for ce in ce_chains_after:
            res_after.append(guenzel23_local_mrt(ce))

        # print(res_before, res_after)

        # if res_before[1]> res_after[2] or res_before[2]<res_after[1]:
        #     print(res_before, res_after)

        # if res_before[-2]-0.000001> res_after[-1] or res_before[-1]<res_after[-2]-0.000001:
        # if res_before[-2]-0.000001> res_after[-1]:
        if res_before[-1]-0.000001 > res_after[-1]:
            taskset.print_tasks()
            print(res_before, res_after)
            breakpoint()

def maketask(period,phase,bcet,wcet):
    return Task('periodic', 'implicit', 'wcet', 'implicit', phase, period, period, period, bcet, wcet, period, None)

def finding1():
    '''3 Tasks: Increasing priority might make result worse.'''
    task0 = maketask(20,0,5,5)
    task1 = maketask(50,0,10,10)
    task2 = maketask(50,0,1,1)
    
    taskset1 = TaskSet(task0, task1, task2)
    ce1 = CEChain(task2, base_ts=taskset1)

    taskset2 = TaskSet(task0, task2, task1)
    ce2 = CEChain(task2,base_ts=taskset2)

    # Check validity
    taskset1.compute_wcrts()
    for tsk in taskset1:
        assert taskset1.wcrts[tsk] <= tsk.deadline
        pass

    taskset2.compute_wcrts()
    for tsk in taskset2:
        assert taskset2.wcrts[tsk] <= tsk.deadline

    # Analysis
    taskset1.schedules = schedule_task_set([ce1], taskset1)[1]
    res1 = guenzel23_local_mrt(ce1)

    taskset2.schedules = schedule_task_set([ce2],taskset2)[1]
    res2 = guenzel23_local_mrt(ce2)


    # Print
    print("Example Taskset with 3 tasks showing that increasing priority can give worse e2e latency:")
    for idx, tsk in enumerate(taskset1):
        print(f" - task{idx}: Period={tsk.period}, Phase={tsk.phase}, BCET={tsk.bcet}, WCET={tsk.wcet}")
    
    print(f"E2E Latency of task2 when having lower priority than tau1: {res1}")
    print(f"E2E Latency of task2 when having higher priority than tau1: {res2}")

def zhishan1():
    '''3 Tasks: Increasing priority might make result worse.'''
    task0 = maketask(20,0,9,9)
    task1 = maketask(25,0,10,10)
    task2 = maketask(50,0,1,1)
    
    taskset1 = TaskSet(task0, task1, task2)
    ce1 = CEChain(task2, base_ts=taskset1)

    taskset2 = TaskSet(task0, task2, task1)
    ce2 = CEChain(task2,base_ts=taskset2)

    # Check validity
    taskset1.compute_wcrts()
    for tsk in taskset1:
        print(taskset1.wcrts[tsk])
        assert taskset1.wcrts[tsk] <= tsk.deadline
        pass

    taskset2.compute_wcrts()
    for tsk in taskset2:
        assert taskset2.wcrts[tsk] <= tsk.deadline

    # Analysis
    taskset1.schedules = schedule_task_set([ce1], taskset1)[1]
    res1 = guenzel23_local_mrt(ce1)

    taskset2.schedules = schedule_task_set([ce2],taskset2)[1]
    res2 = guenzel23_local_mrt(ce2)


    # Print
    print("Example Taskset with 3 tasks showing that increasing priority can give worse e2e latency:")
    for idx, tsk in enumerate(taskset1):
        print(f" - task{idx}: Period={tsk.period}, Phase={tsk.phase}, BCET={tsk.bcet}, WCET={tsk.wcet}")
    
    print(f"E2E Latency of task2 when having lower priority than tau1: {res1}")
    print(f"E2E Latency of task2 when having higher priority than tau1: {res2}")

    
if __name__ == "__main__":
    # search()
    # search2()
    # finding1()
    zhishan1()
    

    
# for taskset in tasksets:
#         adjust_taskset_bcets(taskset, 1.0)
#         taskset.rate_monotonic_scheduling()
#         taskset.compute_wcrts()

# tasksets = remove_invalid_tasksets(tasksets)

