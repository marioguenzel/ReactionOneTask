import PySimpleGUI as sg
import benchmarks.benchmark_WATERS as automotiveBench
import benchmarks.benchmark_Uniform as uniformBench
from e2eAnalyses.Davare2007 import davare07
from e2eAnalyses.Becker2016 import becker16
from e2eAnalyses.Becker2017 import becker17
from e2eAnalyses.Kloda2018 import kloda18
from e2eAnalyses.Duerr2019 import duerr19, duerr_19_mrt, duerr_19_mrda
from e2eAnalyses.Martinez2020 import martinez20_impl, martinez20_let
from e2eAnalyses.Hamann2017 import hamann17
from e2eAnalyses.Guenzel2023_inter import guenzel_23_local_mrt, guenzel_23_local_mda, guenzel_23_local_mrda, guenzel_23_inter
from e2eAnalyses.Guenzel2023_mixed import guenzel_23_mixed
from e2eAnalyses.Bi2022 import bi22
from e2eAnalyses.Kordon2020 import kordon20
import helpers
import plotting.plot as plot
import sys
from multiprocessing import Pool


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
    'becker16' : AnalysisMethod(becker16, 'Becker 2016', 'B16', features=['periodic', 'implicit']),                                                         # TODO
    'hamann17' : AnalysisMethod(hamann17, 'Hamann 2017 (baseline)', 'H17', features=['periodic', 'sporadic', 'let']),
    'becker17' : AnalysisMethod(becker17, 'Becker 2017', 'B17', features=['periodic', 'implicit', 'let']),                                                  # TODO
    'kloda18' : AnalysisMethod(kloda18, 'Kloda 2018', 'K18', features=['periodic', 'implicit']),
    'duerr19_mrt' : AnalysisMethod(duerr_19_mrt, 'Dürr 2019 (MRT)', 'D19(MRT)', features=['periodic', 'sporadic', 'implicit', 'inter']),
    'duerr19_mrda' : AnalysisMethod(duerr_19_mrda, 'Dürr 2019 (MRDA)', 'D19(MRDA)', features=['periodic', 'sporadic', 'implicit', 'inter']),
    'martinez20_impl' : AnalysisMethod(martinez20_impl, 'Martinez 2020 (Impl)', 'M20(Impl)', features=['periodic', 'implicit']),                            # TODO
    'kordon20' : AnalysisMethod(kordon20, 'Kordon 2020', 'K20',features=['periodic', 'let']),                                                               # TODO
    'martinez20_let' : AnalysisMethod(martinez20_let, 'Martinez 2020 (LET)', 'M20(LET)', features=['periodic', 'let']),                                     # TODO
    'bi22' : AnalysisMethod(bi22, 'Bi 2022', 'B22', features=['periodic', 'implicit']),                                                                     # TODO
    'guenzel23_l_mrt' : AnalysisMethod(guenzel_23_local_mrt, 'Günzel 2023 (local MRT)', 'G23(L-MRT)', features=['periodic', 'implicit', 'let']),
    'guenzel23_l_mda' : AnalysisMethod(guenzel_23_local_mda, 'Günzel 2023 (local MDA)', 'G23(L-MDA)', features=['periodic', 'implicit', 'let']),
    'guenzel23_l_mrda' : AnalysisMethod(guenzel_23_local_mrda, 'Günzel 2023 (local MRDA)', 'G23(L-MRDA)', features=['periodic', 'implicit', 'let']),
    'guenzel23_inter' : AnalysisMethod(guenzel_23_inter, 'Günzel 2023 (inter)', 'G23(I)', features=['periodic', 'implicit', 'let', 'inter']),               # TODO
    'guenzel23_mixed' : AnalysisMethod(guenzel_23_mixed, 'Günzel 2023 (mixed)', 'G23(MIX)', features=['periodic', 'sporadic', 'implicit', 'let', 'mixed'])  # TODO
}


def popUp(title, messages):
    view = list(map(lambda message : [sg.T(message)], messages))
    view.append([sg.Push(), sg.B('OK'), sg.Push()])
    sg.Window(title, [view]).read(close=True)


def inititalizeUI():
    sg.theme('system default')

    # Definition of the user interface layout

    layoutMenu = [sg.Menu([['Help', ['Edit Me']], ['About', ['Edit Me']]], k='-MENUBAR-')]

    layoutGeneral = [sg.Frame('General Settings', [
        [sg.Radio('Generate Cause-Effect Chains', "RadioGeneral", default=True, k='-Generate_CEC_Radio-', enable_events=True), sg.Checkbox('Store generated Cause-effect Chains', default=False, k='-Store_CECs_Box-', pad=((60,0),(0,0)))],
        [sg.Radio('Load Cause-Effect Chains from File', "RadioGeneral", default=False, k='-Load_CEC_Radio-', enable_events=True), sg.Text('File:', pad=((35,0),(0,0))), sg.Input(s=30, k='-File_Input-', disabled=True), sg.FileBrowse(file_types=(("Taskset File", "*.pickle"),), k="-Browse-", disabled=True)],
        [sg.Text('Threads:'), sg.Input(s=5, k='-Threads_Input-', default_text='1')],
    ], expand_x=True)]

    layoutTaskset = [sg.Frame('Taskset Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioTaskset", default=True, k='-Automotive_Taskset_Radio-', enable_events=True)],        #   U, #Tasksets?
        [sg.Radio('Uniform Taskset Generation', "RadioTaskset", default=False, k='-Uniform_Taskset_Radio-', enable_events=True)], #   n, U*, #Tasksets?
            [sg.Checkbox('Semi-harmonic periods', default=True, k='-Semi_harmonic_Box-', pad=((30,0),(0,0)), disabled=True, enable_events=True)],
            [sg.Text('Min number Tasks:', pad=((35,0),(0,0))), sg.Input(s=5, k='-MINT_Input-', disabled=True, default_text='40'), sg.Text('Max number Tasks:'), sg.Input(s=5, k='-MAXT_Input-', disabled=True, default_text='60')],
            [sg.Text('Min Period:', pad=((35,0),(0,0))), sg.Input(s=10, k='-PMIN_Input-', disabled=True, default_text='1'), sg.Text('Max Period:'), sg.Input(s=10, k='-PMAX_Input-', disabled=True, default_text='2000')],
        [sg.Text('Target Utilization:'), sg.Spin(values=[i for i in range(0, 101)], initial_value=50, key='-Utilization_Spin-', s=(5,1))],
        [sg.Text('Number of Tasksets:'), sg.Input(s=10, k='-Number_Tasksets_Input-', default_text='1')],
    ], expand_x=True)]

    layoutChain = [sg.Frame('Cause-Effect Chain Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioChain", default=True, k='-Automotive_CEC_Radio-', enable_events=True)],
        [sg.Radio('Random CECs', "RadioChain", default=False, k='-Random_CEC_Radio-', enable_events=True), sg.Text('Min Tasks:'), sg.Input(s=5, k='-Number_Tasks_Min_Input-', default_text='2', disabled=True), sg.Text('Max Tasks:'), sg.Input(s=5, k='-Number_Tasks_Max_Input-', default_text='10', disabled=True)],
        [sg.Text('Min Chains:'), sg.Input(s=5, k='-Number_Chains_Min_Input-', default_text='30'), sg.Text('Max Chains:'), sg.Input(s=5, k='-Number_Chains_Max_Input-', default_text='60')]
    ], expand_x=True)]

    layoutAnalysis = [sg.Frame('Analysis Configuration', [
        [sg.TabGroup([[
            sg.Tab('Implicit Communication',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k=method_key)] for method_key, method in analysesDict.items() if 'implicit' in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            ), 
            sg.Tab('LET Communication',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k=method_key)] for method_key, method in analysesDict.items() if 'let' in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            )
        ]], expand_x=True),
        sg.TabGroup([[
            sg.Tab('Implicit Communication',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k='n_'+method_key)] for method_key, method in analysesDict.items() if 'implicit' in method.features],  
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            ),  
            sg.Tab('LET Communication',[[sg.Column(
                [[sg.Checkbox(method.name, default=False, k='n_'+method_key)] for method_key, method in analysesDict.items() if 'let' in method.features], 
                expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]
            )
        ]], expand_x=True)
        ]
    ], expand_x=True)]

    layoutPlot = [sg.Frame('Plot Configuration', [
        [sg.Checkbox('create normalized plots (relative latency reduction)', default=True, k='-CBP1-')],
        [sg.Checkbox('create absolute plots', default=False, k='-CBP2-')],
        [sg.Checkbox('export raw analyses results (CSV)', default=False, k='-CBP3-')]
    ], expand_x=True, expand_y=True)]

    ttk_style = 'default'

    layout = [
        [layoutMenu],
        [layoutGeneral],
        [layoutTaskset],
        [layoutChain],
        [layoutAnalysis],
        [layoutPlot],
        [sg.Button('Run'), sg.Button('Cancel')]
    ]

    font = ("Arial", 11)
    window = sg.Window('Evaluation Framework for End-to-End Analysis', layout, font=font, ttk_theme=ttk_style)
    return window


def updateUI(window, event, values):
    if event == '-Generate_CEC_Radio-':
        window['-Store_CECs_Box-'].update(disabled=False)
        window['-File_Input-'].update(disabled=True)
        window['-Browse-'].update(disabled=True)
        window['-Automotive_Taskset_Radio-'].update(disabled=False)
        window['-Uniform_Taskset_Radio-'].update(disabled=False)
        window['-Utilization_Spin-'].update(disabled=False)
        window['-Number_Tasksets_Input-'].update(disabled=False)
        if values['-Uniform_Taskset_Radio-']:
            window['-Semi_harmonic_Box-'].update(disabled=False)
            window['-MINT_Input-'].update(disabled=False)
            window['-MAXT_Input-'].update(disabled=False)
            window['-PMIN_Input-'].update(disabled=False)
            window['-PMAX_Input-'].update(disabled=False)
        if values['-Semi_harmonic_Box-']:
            window['-Automotive_CEC_Radio-'].update(disabled=False)
        window['-Random_CEC_Radio-'].update(disabled=False)
        if values['-Random_CEC_Radio-']:
            window['-Number_Tasks_Min_Input-'].update(disabled=False)
            window['-Number_Tasks_Max_Input-'].update(disabled=False)
        window['-Number_Chains_Min_Input-'].update(disabled=False)
        window['-Number_Chains_Max_Input-'].update(disabled=False)

    if event == '-Load_CEC_Radio-':
        window['-Store_CECs_Box-'].update(disabled=True)
        window['-File_Input-'].update(disabled=False)
        window['-Browse-'].update(disabled=False)
        window['-Automotive_Taskset_Radio-'].update(disabled=True)
        window['-Uniform_Taskset_Radio-'].update(disabled=True)
        window['-Utilization_Spin-'].update(disabled=True)
        window['-Number_Tasksets_Input-'].update(disabled=True)
        window['-Semi_harmonic_Box-'].update(disabled=True)
        window['-MINT_Input-'].update(disabled=True)
        window['-MAXT_Input-'].update(disabled=True)
        window['-PMIN_Input-'].update(disabled=True)
        window['-PMAX_Input-'].update(disabled=True)
        window['-Automotive_CEC_Radio-'].update(disabled=True)
        window['-Random_CEC_Radio-'].update(disabled=True)
        window['-Number_Tasks_Min_Input-'].update(disabled=True)
        window['-Number_Tasks_Max_Input-'].update(disabled=True)
        window['-Number_Chains_Min_Input-'].update(disabled=True)
        window['-Number_Chains_Max_Input-'].update(disabled=True)

    if event == '-Automotive_Taskset_Radio-':
        window['-Semi_harmonic_Box-'].update(disabled=True)
        window['-MINT_Input-'].update(disabled=True)
        window['-MAXT_Input-'].update(disabled=True)
        window['-PMIN_Input-'].update(disabled=True)
        window['-PMAX_Input-'].update(disabled=True)

    if event == '-Uniform_Taskset_Radio-':
        window['-Semi_harmonic_Box-'].update(disabled=False)
        window['-MINT_Input-'].update(disabled=False)
        window['-MAXT_Input-'].update(disabled=False)
        window['-PMIN_Input-'].update(disabled=False)
        window['-PMAX_Input-'].update(disabled=False)

    if event == '-Automotive_CEC_Radio-':
        window['-Number_Tasks_Min_Input-'].update(disabled=True)
        window['-Number_Tasks_Max_Input-'].update(disabled=True)

    if event == '-Random_CEC_Radio-':
        window['-Number_Tasks_Min_Input-'].update(disabled=False)
        window['-Number_Tasks_Max_Input-'].update(disabled=False)

    if event == '-Semi_harmonic_Box-':
        if values['-Semi_harmonic_Box-']:
            window['-Automotive_CEC_Radio-'].update(disabled=False)
        else:
            window['-Automotive_CEC_Radio-'].update(disabled=True)
            window['-Random_CEC_Radio-'].update(value=True)




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

        with Pool(number_of_threads) as pool:
            latencies_single = pool.map(method.analysis, cause_effect_chains)
        
        latencies_all.append(latencies_single)
        method.latencies = latencies_single

        # check if result can be reused for other analyses
        ... #TODO

    return latencies_all


def runVisualMode(window):

    while True:
        event, values = window.read()
        updateUI(window, event, values)

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        if event == 'Run':

            ##################################
            ### Gather all inputs from GUI ###
            ##################################

            generate_cecs = values['-Generate_CEC_Radio-']
            store_generated_cecs = values['-Store_CECs_Box-']
            load_cecs_from_file = values['-Load_CEC_Radio-']
            try:
                number_of_threads = int(values['-Threads_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of threads '{values['-Threads_Input-']}'!"])
                continue
            cecs_file_path = values['-File_Input-']
            use_automotive_taskset = values['-Automotive_Taskset_Radio-']
            use_uniform_taskset_generation = values['-Uniform_Taskset_Radio-']
            try:
                target_utilization = int(values['-Utilization_Spin-'])/100
                if target_utilization > 1 or target_utilization < 0:
                    raise ValueError
            except ValueError:
                popUp('ValueError', [f"Invalid target utilization '{values['-Utilization_Spin-']}'!"])
                continue
            try:
                number_of_tasksets = int(values['-Number_Tasksets_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of tasksets '{values['-Number_Tasksets_Input-']}'!"])
                continue
            use_semi_harmonic_periods = values['-Semi_harmonic_Box-']
            try:
                min_number_of_tasks = int(values['-MINT_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of min tasks '{values['-MINT_Input-']}'!"])
                continue
            try:
                max_number_of_tasks = int(values['-MAXT_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of max tasks '{values['-MAXT_Input-']}'!"])
                continue
            try:
                min_period = int(values['-PMIN_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid min period '{values['-PMIN_Input-']}'!"])
                continue
            try:
                max_period = int(values['-PMAX_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid max period '{values['-PMAX_Input-']}'!"])
                continue
            generate_automotive_cecs = values['-Automotive_CEC_Radio-']
            generate_random_cecs = values['-Random_CEC_Radio-']
            try:
                min_number_tasks_in_chain = int(values['-Number_Tasks_Min_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid min number of tasks '{values['-Number_Tasks_Min_Input-']}'!"])
                continue
            try:
                max_number_tasks_in_chain = int(values['-Number_Tasks_Max_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid max number of tasks '{values['-Number_Tasks_Max_Input-']}'!"])
                continue
            try:
                min_number_of_chains = int(values['-Number_Chains_Min_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid min number of chains '{values['-Number_Chains_Min_Input-']}'!"])
                continue
            try:
                max_number_of_chains = int(values['-Number_Chains_Max_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid max number of chains '{values['-Number_Chains_Max_Input-']}'!"])
                continue
            create_normalized_plots = values['-CBP1-']
            create_absolute_plots = values['-CBP2-']
            save_raw_analyses_results = values['-CBP3-']
            
            selected_analysis_methods = []
            for method in analysesDict.keys():
                if values[method] == True:
                    selected_analysis_methods.append(analysesDict[method])

            selected_normalization_methods = []
            for method in analysesDict.keys():
                if values['n_' + method] == True:
                    selected_normalization_methods.append(analysesDict[method])

            print(values)
            print(selected_analysis_methods)
            print(selected_normalization_methods)

            ##########################################
            ### Check whether all inputs are valid ###
            ##########################################

            #TODO

            ######################
            ### Create Taskset ###
            ######################

            output_dir = helpers.make_output_directory()

            # first create a taskset
            if generate_cecs:
                
                # selected automotive benchmark
                if use_automotive_taskset:                        
                    with Pool(number_of_threads) as pool:
                        tasksets = pool.map(automotiveBench.gen_taskset, [target_utilization] * number_of_tasksets)

                # selected uniform benchmark
                if use_uniform_taskset_generation:
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

                for taskset in tasksets:
                    taskset.rate_monotonic_scheduling()
                    taskset.compute_wcrts()

                # remove tasksets with tasks that miss their deadline
                valid_tasksets = tasksets.copy()
                for taskset in tasksets:
                    for task in taskset:
                        if taskset.wcrts[task] > task.deadline:
                            valid_tasksets.remove(taskset)
                            break
                tasksets = valid_tasksets

            #########################################
            ### Generate/Load Cause Effect Chains ###
            #########################################

            cause_effect_chains = []

            if generate_cecs:
                if generate_automotive_cecs:
                    for taskset in tasksets:
                        cause_effect_chains += automotiveBench.gen_ce_chains(
                            taskset, 
                            min_number_of_chains, 
                            max_number_of_chains
                        )

                if generate_random_cecs:
                    for taskset in tasksets:
                        cause_effect_chains += uniformBench.gen_cause_effect_chains(
                            taskset, 
                            min_number_tasks_in_chain, 
                            max_number_tasks_in_chain, 
                            min_number_of_chains, 
                            max_number_of_chains
                        )

                if store_generated_cecs:
                    helpers.write_data(output_dir + "cause_effect_chains.pickle", cause_effect_chains)

            # user selected load CECs from file
            if load_cecs_from_file:
                cause_effect_chains = helpers.load_data(cecs_file_path)

            print(len(cause_effect_chains))

            ####################
            ### Run Analyses ###
            ####################

            performAnalyses(cause_effect_chains, selected_analysis_methods + selected_normalization_methods, number_of_threads)

            ########################
            ### Plot the results ###
            ########################

            for method in selected_analysis_methods:
                print(method.name)
                print(method.latencies)

            # normalized plots
            if create_normalized_plots:
                for baseline in selected_normalization_methods:
                    for method in selected_analysis_methods:
                        if method.latencies != []:
                            plot.plot(method.normalize(baseline), 
                                      output_dir + method.name_short + "_normalized_to_" + baseline.name_short + ".pdf", 
                                      title=method.name_short + " (normalized to " + baseline.name_short + ")"
                            )

                    # only do comparison if there is something to compare
                    if len(selected_analysis_methods) >= 2:
                        plot.plot([method.normalize(baseline) for method in selected_analysis_methods], 
                                  output_dir + "normalized_to_" + baseline.name_short + ".pdf", 
                                  xticks=[method.name_short for method in selected_analysis_methods], 
                                  title="Relative Comparison (normalized to " + baseline.name_short + ")")

            # absolute plots
            if create_absolute_plots:
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


            if save_raw_analyses_results:
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

            #######################
            ### Feedback pop-up ###
            #######################

            popUp('Info', 
                ['Run finished without any errors.', 
                'Results are saved in:', 
                output_dir]
            )


if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) == 0:
        print("User did not pass any arguments (launching GUI-mode)")
        window = inititalizeUI()
        runVisualMode(window)
        window.close()

    if len(args) > 0:
        print("User specified following arguments (launching CLI-mode):")
        print(args)
        #TODO: check if args are valid
        #TODO: launch cli-mode

