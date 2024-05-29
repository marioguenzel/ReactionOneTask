"""
Task set generation with UUNIFAST benchmark.

From the paper: 'Measuring the performance of schedulability tests.' (2005).

Implementation based on:
https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
"""

import numpy as np
import random
from tasks.task import Task
from tasks.taskset import TaskSet
from cechains.chain import CEChain


def gen_taskset(
        target_utilization,
        min_number_tasks,
        max_number_tasks,
        min_period,
        max_period,
        use_automotive_periods,
        rounded=False):
    """Main function to generate a task set with the UUniFast algorithm.
    Output: tasksets as given in tasks.taskset.TaskSet
    with tasks as tasks.task.Task
    - periodic
    - implicit communication

    Variables:

    """

    number_tasks = random.randrange(min_number_tasks, max_number_tasks+1)
    utilizations = uunifast(number_tasks, target_utilization)

    if use_automotive_periods:
        automotive_periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000]
        periods = generate_periods_loguniform_discrete(number_tasks, min_period, max_period, automotive_periods)

    else:
        periods = generate_periods_uniform(number_tasks, min_period, max_period, rounded)
        
    # Create taskset by matching both of the above.
    tasks = []
    for i in range(number_tasks):
        task = Task(
            release_pattern='periodic', 
            deadline_type='implicit', 
            execution_behaviour='wcet', 
            communication_policy='implicit', 
            phase=0, 
            min_iat=periods[i], 
            max_iat=periods[i], 
            period=periods[i], 
            bcet=utilizations[i]*periods[i], 
            wcet=utilizations[i]*periods[i], 
            deadline=periods[i], 
            priority=None
        )
        tasks.append(task)

    return TaskSet(*tasks)


def gen_cause_effect_chains(
        task_set, 
        number_tasks_min, 
        number_tasks_max, 
        number_chains_min, 
        number_chains_max):
    cause_effect_chains = []

    if number_chains_min == number_chains_max:
        number_chains = number_chains_min
    else:
        number_chains = np.random.randint(number_chains_min, number_chains_max)

    for _ in range(number_chains):
        tasks_in_chain = []

        if number_tasks_min == number_tasks_max:
            number_tasks = number_tasks_min
        else:
            number_tasks = np.random.randint(number_tasks_min, number_tasks_max)

        tasks_in_chain = random.sample(task_set.lst, number_tasks)
        random.shuffle(tasks_in_chain)
        cause_effect_chains.append(CEChain(*tasks_in_chain, base_ts=task_set))

    return cause_effect_chains


# help functions


def uunifast(num_tasks, utilization):
        """UUNIFAST utilization pulling."""
        utilizations = []
        cumulative_utilization = utilization
        for i in range(1, num_tasks):
            # Randomly set next utilization.
            cumulative_utilization_next = (
                cumulative_utilization
                * random.random() ** (1.0/(num_tasks-i)))
            utilizations.append(
                cumulative_utilization - cumulative_utilization_next)
            # Compute remaining utilization.
            cumulative_utilization = cumulative_utilization_next
        utilizations.append(cumulative_utilization_next)
        # Return list of utilizations.
        return utilizations


def generate_periods_uniform(num_tasks, min_period,
                             max_period, rounded=False):
    """Generate uniformly distributed periods to create tasks.

    Variables:
    num_tasks: number of tasks per set
    min_period: minimal period
    max_period: maximal period
    rounded: flag to round periods to integers
    """
    # Create random periods.
    periods = np.random.uniform(
        low=min_period,
        high=max_period,
        size=num_tasks)

    if rounded:  # round periods to nearest integer
        return np.rint(periods).tolist()
    else:
        return periods.tolist()


def generate_periods_loguniform(num_tasks, min_period,
                                max_period, rounded=False):
    """Generate log-uniformly distributed periods to create tasks.

    Variables:
    num_tasks: number of tasks per set
    min_period: minimal period
    max_period: maximal period
    rounded: flag to round periods to integers
    """
    # Create random periods.
    periods = np.exp(np.random.uniform(
        low=np.log(min_period),
        high=np.log(max_period),
        size=num_tasks))

    if rounded:  # round periods to nearest integer
        return np.rint(periods).tolist()
    else:
        return periods.tolist()


def generate_periods_loguniform_discrete(num_tasks, min_period,
                                         max_period, round_down_set):
    """Generate log-uniformly distributed periods to create tasks.

    Variables:
    num_tasks: number of tasks per set
    min_period: minimal period
    max_period: maximal period
    round_down_set: predefined periods
    """
    # Create periods log-uniformly.
    periods = generate_periods_loguniform(
        num_tasks, min_period, max_period, rounded=False)
    # Round down to the entries of round_down_set.
    rounded_periods = []
    round_down_set.sort(reverse=True)
    for p in periods:
        for r in round_down_set:
            if p >= r:
                rp = r
                break
        rounded_periods.append(rp)
    # Return the set of periods.
    return rounded_periods