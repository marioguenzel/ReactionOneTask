from tasks.task import Task
import yaml

class TaskExport:
    """Export format for a single task"""

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

class CEC_Export:
    """Export format for a local cause-effect chain"""

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


class Inter_CEC_Export:
    """Export format for an interconnected cause-effect chain"""

    def __init__(self, cause_effect_chains):
        self.Tasks = []
        self.Chains = []

        # store cecs
        tasksets = set()
        for inter_chain in cause_effect_chains:
            inter_chain_ids = []
            for local_chain in inter_chain:
                tasksets.add(local_chain.base_ts)
                inter_chain_ids.extend(local_chain.id_list())
            self.Chains.append(inter_chain_ids)

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
    """Saves the given cause-effect chains and the underlying task
    sets in a yaml file at the passed output_path
    """

    yaml.add_representer(TaskExport, task_export_representer)

    with open(f'{output_path}cause_effect_chains.yaml', 'w') as yaml_file:
        if isinstance(cause_effect_chains[0], tuple):
            obj = Inter_CEC_Export(cause_effect_chains)
        else:
            obj = CEC_Export(cause_effect_chains)
        yaml.dump(obj.__dict__, yaml_file, default_flow_style=None, width=1000)

    return f'{output_path}chains.yaml'
