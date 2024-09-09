"""
Basis from https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed/blob/master/e2e/cechains/chain.py
"""

from tasks.taskset import TaskSet


class CEChain(TaskSet):
    """A cause-effect chain."""

    def __init__(self, *args, base_ts=None):
        self.base_ts = base_ts  # base task set (needed for some analyses)
        super().__init__(*args)

    def length(self):
        """returns the length of the cec"""

        return len(self._lst)
    
    def contains(self, task):
        """checks if the given task is in the cec"""

        return self._lst.count(task) > 0
    
    def id_list(self):
        """returns the list of task ids in the cec"""

        ids = []
        for task in self._lst:
            ids.append(int(task.id))
        return ids

