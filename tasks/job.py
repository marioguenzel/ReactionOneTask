from tasks.task import Task

class Job:

    def __init__(self, task, occurrence):
        self.task = task
        self.occurrence = occurrence

    def get_release(self):
        return self.task.period * self.occurrence
    
    def get_deadline(self):
        return self.get_release() + self.task.deadline