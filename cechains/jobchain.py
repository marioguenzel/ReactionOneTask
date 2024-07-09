from tasks.job import Job


#####
# Abstract integer conversion
#####

def jc_to_abstr(job_chain):
    abstr = []
    for job in job_chain:
        abstr.append(job.occurrence)
    return abstr


def abstr_to_jc(abstr, ce_chain):
    jobs = []
    for task, occurrence in zip(ce_chain, abstr):
        jobs.append(Job(task, occurrence))
    return JobChain(*jobs)


#####
# Job chain definitions
#####

class JobChain(list):
    """A chain of jobs."""

    def __init__(self, *jobs):
        """Create a job chain with jobs *jobs."""
        super().__init__(jobs)

    def __str__(self, no_braces=False):
        return "[ " + " -> ".join([str(j) for j in self]) + " ]"



class PartitionedJobChain:
    """A partitioned job chain."""

    def __init__(self, chain, fw, bw):
        self.bw = bw
        self.fw = fw
        self.complete = self.bw[0].occurrence >= 0  # complete iff bw chain complete
        self.base_ce_chain = chain

    def __str__(self):
        entries = [self.bw.__str__(no_braces=True), self.fw.__str__(no_braces=True)]
        return "[ " + " / ".join(entries) + " ]"
