import subprocess
from utilities.yaml_export_gohary import export_to_yaml
from utilities.csv_import_gohary import get_latencies_from_csv

# enables debug/error output of system calls
debug_messages = False
error_messages = False

def gohary22(cause_effect_chains):
    latencies = []

    # downloads the implementation from gohary
    result = subprocess.run(
        ["git", "clone", "git@github.com:porya-gohary/np-data-age-analysis.git", "external/gohary/"],
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
        ["git", "-C", "external/gohary/", "checkout 6516f9e"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if debug_messages:
        print("Output:", result.stdout)
    if error_messages:
        print("Error:", result.stderr)

    # downloads submodules of gohary's analysis
    result = subprocess.run(
        ["git", "-C", "external/gohary/", "submodule", "update", "--init", "--recursive"],
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
        ["cmake", "-Bexternal/gohary/build", "-Sexternal/gohary"],
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
        ["make", "-C", "external/gohary/build", "-j"],
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

    # run gohary once per taskset
    for taskset in taskset_cecs:
        # export values to goharys input yaml format
        yaml_path = export_to_yaml('external/gohary/', taskset_cecs[taskset])

        # run gohary with yaml file
        subprocess.run(
            ["./external/gohary/build/run_analysis", yaml_path, "-w"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if debug_messages:
            print("Output:", result.stdout)
        if error_messages:
            print("Error:", result.stderr)

        # parse the return values
        latencies_single = (get_latencies_from_csv('results_DA.csv'))

        # analysis method does not always return plausible values, default fallback to 0
        if len(latencies_single) < len(taskset_cecs[taskset]):
            latencies_single = [0] * len(taskset_cecs[taskset])

        latencies.extend(latencies_single)

    return latencies