#!/usr/bin/env python3

"""
Basis from https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed/blob/master/e2e/tasks/task.py
"""

import uuid

####################
# Task.
####################
class Task:
    """A task."""
    features = {  # list of possible features and their values
        'release_pattern': ['sporadic', 'periodic'],
        'deadline_type': ['arbitrary', 'constrained', 'implicit'],
        'execution_behaviour': ['wcet', 'bcet', 'wc', 'bc', 'bcwc'],
        'communication_policy': ['implicit', 'explicit', 'LET'],
    }

    def __init__(self,
                 release_pattern,
                 deadline_type,
                 execution_behaviour,
                 communication_policy,
                 phase,
                 min_iat,
                 max_iat,
                 period,
                 bcet,
                 wcet,
                 deadline,
                 priority
                ):

        if release_pattern not in self.features['release_pattern']:
            raise ValueError(f'{release_pattern} is not a possible argument.')
        
        if deadline_type not in self.features['deadline_type']:
            raise ValueError(f'{deadline_type} is not a possible argument.')
        
        if execution_behaviour not in self.features['execution_behaviour']:
            raise ValueError(f'{execution_behaviour} is not a possible argument.')
        
        if communication_policy not in self.features['communication_policy']:
            raise ValueError(f'{communication_policy} is not a possible argument.')

        self.id = uuid.uuid4()  # necessary for multiprocessing
        self.release_pattern = release_pattern
        self.deadline_type = deadline_type
        self.execution_behaviour = execution_behaviour
        self.communication_policy = communication_policy
        self.phase = phase
        self.min_iat = min_iat
        self.max_iat = max_iat
        self.period = period
        self.bcet = bcet
        self.wcet = wcet
        self.deadline = deadline
        self.priority = priority
        self.jitter = 0         # TODO


    def print(self):
        """Quick print of all attributes for debugging."""
        # print(self)
        print(vars(self))


    def utilization(self):
        """Task utilization."""
        return (self.wcet / self.min_iat)
    

    def copy(self):
        return Task(
            self.release_pattern,
            self.deadline_type,
            self.execution_behaviour,
            self.communication_policy,
            self.phase,
            self.min_iat,
            self.max_iat,
            self.period,
            self.bcet,
            self.wcet,
            self.deadline,
            self.priority
        )

