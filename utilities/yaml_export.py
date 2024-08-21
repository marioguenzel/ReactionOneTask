from tasks.task import Task
import yaml

class TaskExport:
    def __init__(self, task : Task, taskset):
        self.TaskID = int(task.id)
        self.ReleasePattern = task.release_pattern
        self.DeadlineType = task.deadline_type
        self.ExecutionBehaviour = task.execution_behaviour
        self.CommunicationPolicy = task.communication_policy
        self.Phase = task.phase
        self.BCET = task.bcet
        self.WCET = task.wcet
        self.Period = task.period
        self.MinIAT = task.min_iat
        self.MaxIAT = task.max_iat
        self.Deadline = task.deadline
        self.Priority = task.priority
        self.ECU = int(taskset.id)
        self.Jitter = task.jitter

class Export:
    def __init__(self, cause_effect_chains):
        self.Tasks = []
        self.Chains = []

        # store cecs
        tasksets = set()
        for chain in cause_effect_chains:
            tasksets.add(chain.base_ts)
            self.Chains.append(chain.id_list())

        # store tasks
        task_dict = dict()
        for taskset in tasksets:
            for task in taskset:
                taskExport = TaskExport(task, taskset)
                self.Tasks.append(taskExport)
                task_dict[task.id] = task


def task_export_representer(dumper, data):
    return dumper.represent_mapping('!Task', data.__dict__)


def export_to_yaml(output_path, cause_effect_chains):

    yaml.add_representer(TaskExport, task_export_representer)

    with open(f'{output_path}chains.yaml', 'w') as yaml_file:
        obj = Export(cause_effect_chains)
        yaml.dump(obj.__dict__, yaml_file, default_flow_style=None, width=1000)

    return f'{output_path}chains.yaml'
