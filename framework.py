import benchmarks.benchmark_WATERS as automotiveBench
import benchmarks.benchmark_Uniform as uniformBench
from e2eAnalyses.Davare2007 import davare07
from e2eAnalyses.Becker2016 import becker16
from e2eAnalyses.Becker2017 import becker17
from e2eAnalyses.Kloda2018 import kloda18
from e2eAnalyses.Duerr2019 import duerr19, duerr_19_mrt, duerr_19_mrda
from e2eAnalyses.Martinez2020 import martinez20_impl, martinez20_let
from e2eAnalyses.Hamann2017 import hamann17
from e2eAnalyses.Guenzel2023_inter import guenzel_23_local_mrt, guenzel_23_local_mda, guenzel_23_local_mrda, guenzel_23_inter_mrt, guenzel_23_inter_mrda
from e2eAnalyses.Guenzel2023_mixed import guenzel_23_mix_pessimistic, guenzel_23_mix, guenzel_23_mix_improved
from e2eAnalyses.Guenzel2023_equi import guenzel_23_equi_mda, guenzel_23_equi_mrt
from e2eAnalyses.Bi2022 import bi22
from e2eAnalyses.Kordon2020 import kordon20
from e2eAnalyses.newAnalysis import newAna
import helpers
import plotting.plot as plot
import random as random
from multiprocessing import Pool


class FrameworkOptions:
    def __init__(
            self,
            generate_cecs,
            store_generated_cecs,
            load_cecs_from_file,
            number_of_threads
    ):
        ...


class AnalysisMethod:

    def __init__(self, analysis_function, name, name_short, features):
        self.analysis = analysis_function
        self.name = name
        self.name_short = name_short
        self.features = features
        self.latencies = []

    def reset(self):
        self.latencies = []

    def normalize(self, baseline):
        if len(self.latencies) != len(baseline.latencies):
            return []
        else:
            return [(b-a)/b for a,b in zip(self.latencies, baseline.latencies)]


analysesDict = {
    'davare07' : AnalysisMethod(davare07, 'Davare 2007 (baseline)', 'D07', features=['periodic', 'implicit']),
    'becker16' : AnalysisMethod(becker16, 'Becker 2016', 'B16', features=['periodic', 'implicit']),                                                                                         # TODO
    'hamann17' : AnalysisMethod(hamann17, 'Hamann 2017 (baseline)', 'H17', features=['periodic', 'sporadic', 'let']),
    'becker17_impl' : AnalysisMethod(becker17, 'Becker 2017', 'B17', features=['periodic', 'implicit']),                                                                                  # TODO
    'becker17_let' : AnalysisMethod(becker17, 'Becker 2017', 'B17', features=['periodic', 'let']),                                                                                  # TODO
    'kloda18' : AnalysisMethod(kloda18, 'Kloda 2018', 'K18', features=['periodic', 'implicit']),
    'duerr19_mrt' : AnalysisMethod(duerr_19_mrt, 'Dürr 2019 (MRT)', 'D19(MRT)', features=['periodic', 'sporadic', 'implicit', 'inter']),
    'duerr19_mrda' : AnalysisMethod(duerr_19_mrda, 'Dürr 2019 (MRDA)', 'D19(MRDA)', features=['periodic', 'sporadic', 'implicit', 'inter']),
    'martinez20_impl' : AnalysisMethod(martinez20_impl, 'Martinez 2020 (Impl)', 'M20(Impl)', features=['periodic', 'implicit']),                                                            # TODO
    'kordon20' : AnalysisMethod(kordon20, 'Kordon 2020', 'K20',features=['periodic', 'let']),                                                                                               # TODO
    'martinez20_let' : AnalysisMethod(martinez20_let, 'Martinez 2020 (LET)', 'M20(LET)', features=['periodic', 'let']),                                                                     # TODO
    'bi22' : AnalysisMethod(bi22, 'Bi 2022', 'B22', features=['periodic', 'implicit']),                                                                                                     # TODO
    'guenzel23_l_mrt' : AnalysisMethod(guenzel_23_local_mrt, 'Günzel 2023 (local MRT)', 'G23(L-MRT)', features=['periodic', 'implicit']),
    'guenzel23_l_mda' : AnalysisMethod(guenzel_23_local_mda, 'Günzel 2023 (local MDA)', 'G23(L-MDA)', features=['periodic', 'implicit']),
    'guenzel23_l_mrda' : AnalysisMethod(guenzel_23_local_mrda, 'Günzel 2023 (local MRDA)', 'G23(L-MRDA)', features=['periodic', 'implicit']),
    'guenzel_23_inter_mrt' : AnalysisMethod(guenzel_23_inter_mrt, 'Günzel 2023 (inter MRT)', 'G23(I-MRT)', features=['periodic', 'implicit', 'inter']),                              # TODO
    'guenzel_23_inter_mrda' : AnalysisMethod(guenzel_23_inter_mrda, 'Günzel 2023 (inter MRDA)', 'G23(I-MRDA)', features=['periodic', 'implicit', 'inter']),                          # TODO
    'guenzel23_mixed_pess' : AnalysisMethod(guenzel_23_mix_pessimistic, 'Günzel 2023 (mixed, pessimistic)', 'G23(MIX-P)', features=['periodic', 'sporadic', 'implicit', 'let', 'mixed']),
    'guenzel23_mixed' : AnalysisMethod(guenzel_23_mix, 'Günzel 2023 (mixed)', 'G23(MIX)', features=['periodic', 'sporadic', 'implicit', 'let', 'mixed']),
    'guenzel23_mixed_imp' : AnalysisMethod(guenzel_23_mix_improved, 'Günzel 2023 (mixed, improved)', 'G23(MIX-I)', features=['periodic', 'sporadic', 'implicit', 'let', 'mixed']),
    'guenzel_23_equi_mda': AnalysisMethod(guenzel_23_equi_mda, 'Günzel 2023 (equi, MDA)', 'G23(EQUI-MDA)', features=['periodic', 'sporadic', 'let']),
    'guenzel_23_equi_mrt': AnalysisMethod(guenzel_23_equi_mrt, 'Günzel 2023 (equi, MRT)', 'G23(EQUI-MRT)', features=['periodic', 'sporadic', 'let']),
    'newAna': AnalysisMethod(newAna, 'newAna', 'newAna', features=['periodic', 'sporadic', 'implicit']),
}



def normalizeLatencies(toNormalize, baseline):
    return [(b-a)/b for a,b in zip(toNormalize, baseline)]


def performAnalyses(cause_effect_chains, methods, number_of_threads):
    latencies_all = []

    # delete values from previous runs
    for method in methods:
        method.reset()

    # compute new latencies
    for method in methods:
        if method == None:
            # method is not yet implemented
            latencies_all.append([])
            continue

        if method.latencies != []:
            # latencies have been computed by another analysis method
            latencies_all.append(method.latencies)
            continue

        if isinstance(cause_effect_chains[0], tuple):
            with Pool(number_of_threads) as pool:
                latencies_single = pool.starmap(method.analysis, cause_effect_chains)
        else:
            with Pool(number_of_threads) as pool:
                latencies_single = pool.map(method.analysis, cause_effect_chains)
        
        latencies_all.append(latencies_single)
        method.latencies = latencies_single

        # check if result can be reused for other analyses
        ... #TODO

    return latencies_all


def create_interconnected_cecs(cause_effect_chains, min_ecus, max_ecus, number_of_chains):
    interconncected_chains = []
    print(cause_effect_chains)

    while len(interconncected_chains) < number_of_chains:
        n = random.randint(min_ecus, max_ecus)
        candidates = random.sample(cause_effect_chains, n)
        
        # only add candidate if cecs have different base ts
        tasksets = set([cec.base_ts for cec in candidates])
        if len(tasksets) == n:
            random.shuffle(candidates)
            interconncected_chains.append(tuple(candidates))

    return interconncected_chains


def generate_automotive_tasksets(target_utilization, 
                               number_of_tasksets, 
                               number_of_threads):
    tasksets = []
    with Pool(number_of_threads) as pool:
        tasksets = pool.map(automotiveBench.gen_taskset, [target_utilization] * number_of_tasksets)
    return tasksets


def generate_uniform_tasksets(target_utilization, 
                            min_number_of_tasks, 
                            max_number_of_tasks, 
                            min_period, 
                            max_period, 
                            use_semi_harmonic_periods,
                            number_of_tasksets,
                            number_of_threads):
    tasksets = []
    with Pool(number_of_threads) as pool:
        tasksets = pool.starmap(uniformBench.gen_taskset, [(
            target_utilization, 
            min_number_of_tasks, 
            max_number_of_tasks,
            min_period,
            max_period,
            use_semi_harmonic_periods,
            False
        )] * number_of_tasksets)
    return tasksets


def remove_invalid_tasksets(tasksets):
    valid_tasksets = tasksets.copy()
    for taskset in tasksets:
        for task in taskset:
            if taskset.wcrts[task] > task.deadline:
                valid_tasksets.remove(taskset)
                break
    tasksets = valid_tasksets
    return tasksets


def adjust_taskset_release_pattern(taskset, sporadic_ratio):
    for task in random.sample(taskset.lst, int(len(taskset.lst) * sporadic_ratio)):
        task.release_pattern = 'sporadic'


def adjust_taskset_communication_policy(taskset, let_ratio):
    for task in random.sample(taskset.lst, int(len(taskset.lst) * let_ratio)):
        task.communication_policy = 'LET'


def generate_automotive_cecs(tasksets, min_number_of_chains, max_number_of_chains):
    cause_effect_chains = []
    for taskset in tasksets:
        cause_effect_chains += automotiveBench.gen_ce_chains(taskset, 
                                                             min_number_of_chains, 
                                                             max_number_of_chains)
    return cause_effect_chains


def generate_random_cecs(tasksets, 
                       min_number_tasks_in_chain, 
                       max_number_tasks_in_chain, 
                       min_number_of_chains, 
                       max_number_of_chains):
    cause_effect_chains = []
    for taskset in tasksets:
        cause_effect_chains += uniformBench.gen_cause_effect_chains(
            taskset, 
            min_number_tasks_in_chain, 
            max_number_tasks_in_chain, 
            min_number_of_chains, 
            max_number_of_chains
        )
    return cause_effect_chains


def create_normalized_plots(selected_analysis_methods, 
                            selected_normalization_methods, 
                            output_dir):
    for baseline in selected_normalization_methods:
        for method in selected_analysis_methods:
            if method.latencies != []:
                plot.plot(method.normalize(baseline), 
                            output_dir + method.name_short + "_normalized_to_" + baseline.name_short + ".pdf", 
                            title=method.name_short + " (normalized to " + baseline.name_short + ")",
                            ylimits=(0, 1.0)
                )

        # only do comparison if there is something to compare
        if len(selected_analysis_methods) >= 2:
            plot.plot([method.normalize(baseline) for method in selected_analysis_methods], 
                        output_dir + "normalized_to_" + baseline.name_short + ".pdf", 
                        xticks=[method.name_short for method in selected_analysis_methods], 
                        title="Relative Comparison (normalized to " + baseline.name_short + ")",
                        ylimits=(0, 1.0))


def create_absolute_plots(selected_analysis_methods, 
                          output_dir):
    for method in selected_analysis_methods:
        if method.latencies != []:
            plot.plot(method.latencies, output_dir + method.name_short + ".pdf")

    # only do comparison if there is something to compare
    if len(selected_analysis_methods) >= 2:
        plot.plot([method.latencies for method in selected_analysis_methods], 
                    output_dir + "absolute.pdf", 
                    xticks=[method.name_short for method in selected_analysis_methods], 
                    title="Absolute Comparison"
        )


def save_raw_analysis_results(selected_analysis_methods,
                              selected_normalization_methods,
                              output_dir):
    selected_methods = set(selected_analysis_methods + selected_normalization_methods)
    names_all = []
    latencies_all = []
    for method in selected_methods:
        names_all.append(method.name_short)
        latencies_all.append(method.latencies)

    helpers.export_to_csv(
        output_dir + "results.csv",
        names_all,
        latencies_all
    )


