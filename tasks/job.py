from tasks.task import Task

class Job:

    def __init__(self, task, occurrence):
        self.task = task
        self.occurrence = occurrence