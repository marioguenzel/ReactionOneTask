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
    
    def id_list(self):
        ids = []
        for task in self._lst:
            ids.append(int(task.id))
        return ids
    
    def copy(self):
        new_tasks = []
        new_tasks_dict = dict()
        for task in self.base_ts:
            new_task = task.copy()
            new_task.id = task.id
            new_tasks.append(new_task)
            new_tasks_dict[new_task.id] = new_task
        
        new_base_ts = TaskSet(*new_tasks)
        new_base_ts.id = self.base_ts.id
        cec_list = []
        for task in self._lst:
            cec_list.append(new_tasks_dict[task.id])
        new_cec = CEChain(*cec_list, base_ts=new_base_ts)

        return new_cec


if __name__ == '__main__':
    from tasks.task import Task

    ce = CEChain(Task(), Task(), Task())
    breakpoint()
