"""
Analysis from Gohari et al.:
Data-Age Analysis for Multi-Rate Task Chains under Timing Uncertainty

Please note that the code procuces a local copy of the analysis by Gohari et al.: 
https://github.com/porya-gohary/np-data-age-analysis
Since the repository by Gohari et al. is published under BSD 3 license, the local 
copy of it is subject to the BSD 3 license as well.

- implicit
- periodic
"""


import subprocess
from utilities.yaml_export_gohari import export_to_yaml
from utilities.csv_import_gohari import get_latencies_from_csv

# enables debug/error output of system calls
debug_messages = False
error_messages = False

def gohari22(cause_effect_chains):
    latencies = []

    # downloads the implementation from gohari
    result = subprocess.run(
        ["git", "clone", "https://github.com/porya-gohary/np-data-age-analysis.git", "external/gohari/"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if debug_messages:
        print("Output:", result.stdout)
    if error_messages:
        print("Error:", result.stderr)

    # switches to the commit that is known to work with the evaluation framework
    result = subprocess.run(
        ["git", "-C", "external/gohari/", "checkout", "6516f9e"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if debug_messages:
        print("Output:", result.stdout)
    if error_messages:
        print("Error:", result.stderr)

    # downloads submodules of gohari's analysis
    result = subprocess.run(
        ["git", "-C", "external/gohari/", "submodule", "update", "--init", "--recursive"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if debug_messages:
        print("Output:", result.stdout)
    if error_messages:
        print("Error:", result.stderr)

    # cmake to generate makefile
    result = subprocess.run(
        ["cmake", "-Bexternal/gohari/build", "-Sexternal/gohari"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if debug_messages:
        print("Output:", result.stdout)
    if error_messages:
        print("Error:", result.stderr)

    # build the project
    result = subprocess.run(
        ["make", "-C", "external/gohari/build", "-j"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if debug_messages:
        print("Output:", result.stdout)
    if error_messages:
        print("Error:", result.stderr)


    # generate taskset -> cecs dictionary
    taskset_cecs = dict()
    for cause_effect_chain in cause_effect_chains:
        if cause_effect_chain.base_ts in taskset_cecs.keys():
            taskset_cecs[cause_effect_chain.base_ts].append(cause_effect_chain)
        else:
            taskset_cecs[cause_effect_chain.base_ts] = [cause_effect_chain]

    # run gohari once per taskset
    for taskset in taskset_cecs:
        # export values to goharis input yaml format
        yaml_path = export_to_yaml('external/gohari/', taskset_cecs[taskset])

        # run gohari with yaml file
        subprocess.run(
            ["./external/gohari/build/run_analysis", yaml_path, "-w"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if debug_messages:
            print("Output:", result.stdout)
        if error_messages:
            print("Error:", result.stderr)

        try:
            # parse the return values
            latencies_single = (get_latencies_from_csv('results_DA.csv'))

        except FileNotFoundError:
            # analysis method does not always return values, because task set could be not 
            # schedulable under non-preemptive scheduling
            latencies_single = [-1] * len(taskset_cecs[taskset])

        latencies.extend(latencies_single)

    return latencies
