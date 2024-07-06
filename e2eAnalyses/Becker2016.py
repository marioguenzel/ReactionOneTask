"""
Analysis from Becker et al. 2016:
Synthesizing Job-Level Dependencies for Automotive Multi-rate Effect Chains.

- implicit
- periodic
"""

from tasks.task import Task
from cechains.chain import CEChain

# helpers

def get_dmin(job):
    ...
    # TODO

def get_rmin(job):
    ...
    # TODO

def get_rmax(job):
    ...
    # TODO


class DPT_Vertex:

    def __init__(self, job):
        self.job = job
        self.max_branch_age = None
        self.final_node = False
        self.incomming = []         # list of all incomming edges   [(vertex, valid)]
        self.outgoing = []          # list of all outgoing edges    [(vertex, valid)]

    @property
    def final_node(self):
        return self.final_node

    @final_node.setter
    def final_node(self, final_node):
        self.final_node = final_node

    @property
    def max_branch_age(self):
        return self.max_branch_age

    @max_branch_age.setter
    def max_branch_age(self, max_branch_age):
        self.max_branch_age = max_branch_age

    @property
    def job(self):
        return self.job

    @job.setter
    def job(self, job):
        self.job = job
    
    def set_branch_age(self, root_node, init_type):
        if init_type == 3:
            self.max_branch_age = get_dmin(self.job) - get_rmin(root_node)
        else:
            self.max_branch_age = get_rmax(self.job) + self.job.task.wcet - get_rmin(root_node)

    def is_root(self):
        return len(self.incomming) == 0
    
    def is_leaf(self):
        return len(self.outgoing) == 0


class DataPropagationTree:

    def __init__(self, ce_chain, init_type):
        self.chain = ce_chain
        self.init_type = init_type

    def initialize_variables(self):
        ...



def generate_dpt(ce_chain):
    ...

def generate_single_dpt():
    ...

def recursive_dpt(
    dpt : DataPropagationTree, 
    vertex : DPT_Vertex, 
    chain : CEChain
):
    current_task_index = chain.index(vertex.job.task)
    if current_task_index == chain.length-1:
        # end of chain is reached
        # TODO
        ...
    
    successor_task = chain[current_task_index+1]

    possible_successors = get_possible_successors(vertex, successor_task)


    ...

def mark_invalid_edges():
    ...

def get_root(dpt_vertex : DPT_Vertex):
    current_vertex = dpt_vertex
    while not current_vertex.is_root():
        current_vertex = current_vertex.incomming[0][0]
    return current_vertex


def get_possible_successors(dpt_vertex : DPT_Vertex, successor : Task):
    successors = []

    for 
    

def get_initial_jobs():
    ...

def append_job_to_graph():
    ...

def get_vertex():
    ...

def get_chains():
    ...

def get_jobs():
    ...

def get_source_nodes():
    ...




def becker16(chain):

    return -1
