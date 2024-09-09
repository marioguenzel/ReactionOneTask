"""
Utility file for gohari22
Special yaml export with format that suits the implementation from:
https://github.com/porya-gohary/np-data-age-analysis
"""


from tasks.task import Task
import yaml

class TaskExport:
    def __init__(self, task : Task, taskset, task_id):
        # values have to be multiplied by 1000000, because gohari's analysis expects integer values
        # also, task_ids have to begin at 0 and cannot be an arbitrary id
        # same for PEs ids
        self.TaskID = task_id
        self.BCET = int(task.bcet*1000000)
        self.WCET = int(task.wcet*1000000)
        self.Period = int(task.period*1000000)
        self.Deadline = int(task.deadline*1000000)
        self.PE = int(taskset.id)
        self.Jitter = int(task.jitter*1000000)
        self.Successors = []

class Export:
    def __init__(self, cause_effect_chains):
        self.vertexset = []
        self.taskchains = []

        # store cecs
        tasksets = set()
        for chain in cause_effect_chains:
            tasksets.add(chain.base_ts)

        # store tasks and minimize task ids
        task_dict = dict()
        id_map = dict()
        export_task_id = 0
        for taskset in tasksets:
            for task in taskset:
                taskExport = TaskExport(task, taskset, export_task_id)
                id_map[int(task.id)] = export_task_id
                self.vertexset.append(taskExport)
                task_dict[export_task_id] = taskExport
                export_task_id = export_task_id + 1

        # compute successors, needed for gohari 2022
        self.taskchains = []
        for chain in cause_effect_chains:
            id_list = self.translate_ids(chain.id_list(), id_map)
            self.taskchains.append({"Chain": id_list})
            for i in range(1, len(id_list)):
                if id_list[i] not in task_dict[id_list[i-1]].Successors:
                    task_dict[id_list[i-1]].Successors.append(id_list[i])

        # minimize PE ids, since all tasks belong to the same taskset, value of PE
        # is the same for all tasks
        for taskExport in self.vertexset:
            taskExport.PE = 0


    def translate_ids(self, task_list, id_map):
        new_task_list = []
        for task in task_list:
            new_task_list.append(id_map[task])
        return new_task_list


def task_export_representer(dumper, data):
    return dumper.represent_mapping('!Task', data.__dict__)


def export_to_yaml(path, cause_effect_chains):

    yaml.add_representer(TaskExport, task_export_representer)

    with open(f'{path}chains.yaml', 'w') as yaml_file:
        obj = Export(cause_effect_chains)
        yaml.dump(obj.__dict__, yaml_file, default_flow_style=None, width=1000)

    return f'{path}chains.yaml'