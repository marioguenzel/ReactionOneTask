import os
from utilities.yaml_export_gohary import export_to_yaml
from utilities.csv_import_gohary import get_latencies_from_csv


def gohary22(cause_effect_chains):
    latencies = []

    # downloads the implementation from gohary
    os.popen("git clone git@github.com:porya-gohary/np-data-age-analysis.git external/gohary/").read()
    os.popen("git -C external/gohary/ checkout 6516f9e").read()
    os.popen("git -C external/gohary/ submodule update --init --recursive").read()
    os.popen("cmake -Bexternal/gohary/build -Sexternal/gohary").read()
    os.popen("make -C external/gohary/build -j").read()

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
        os.popen(f"./external/gohary/build/run_analysis {yaml_path} -w").read()

        # parse the return values
        latencies_single = (get_latencies_from_csv('results_DA.csv'))

        # analysis method does not always return plausible values, default fallback to 0
        if len(latencies_single) < len(taskset_cecs[taskset]):
            latencies_single = [0] * len(taskset_cecs[taskset])

        print(latencies_single)

        latencies.extend(latencies_single)

    return latencies