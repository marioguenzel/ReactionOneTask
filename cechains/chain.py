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
        return len(self._lst)
    
    def contains(self, task):
        return self._lst.count(task) > 0


if __name__ == '__main__':
    from tasks.task import Task

    ce = CEChain(Task(), Task(), Task())
    breakpoint()
