import PySimpleGUI as sg
import benchmarks.benchmark_WATERS as automotiveBench
import benchmarks.benchmark_Uniform as uniformBench
from e2eAnalyses.Davare2007 import davare07
from e2eAnalyses.Duerr2019 import duerr19, duerr_19_mrt, duerr_19_mrda
from e2eAnalyses.Hamann2017 import hamann17
from e2eAnalyses.Kloda2018 import kloda18
from e2eAnalyses.Guenzel2023_inter import guenzel_23_local_mrt, guenzel_23_local_mda, guenzel_23_local_mrda, guenzel_23_inter
from e2eAnalyses.Guenzel2023_mixed import guenzel_23_mixed
import helpers
import plotting.plot as plot
import sys
from multiprocessing import Pool


class AnalysisMethod:

    def __init__(self, analysis_function, name, name_short):
        self.analysis = analysis_function
        self.name = name
        self.name_short = name_short
        self.latencies = []

    def reset(self):
        self.latencies = []

    def normalize(self, baseline):
        # TODO: maybe error handling, if lengths are not equal
        return [(b-a)/b for a,b in zip(self.latencies, baseline.latencies)]


analysesDict = {
    'davare07' : AnalysisMethod(davare07, 'Davare 2007 (baseline)', 'D07'),
    'becker16' : None,                                                                                          # TODO
    'kloda18' : AnalysisMethod(kloda18, 'Kloda 2018', 'K18'),
    'duerr19_mrt' : AnalysisMethod(duerr_19_mrt, 'Dürr 2019 (MRT)', 'D19(MRT)'),
    'duerr19_mrda' : AnalysisMethod(duerr_19_mrda, 'Dürr 2019 (MRDA)', 'D19(MRDA)'),
    'martinez20_impl' : None,                                                                                   # TODO
    'bi22' : None,                                                                                              # TODO
    'guenzel23_l_mrt' : AnalysisMethod(guenzel_23_local_mrt, 'Günzel 2023 (local MRT)', 'G23(L-MRT)'),
    'guenzel23_l_mda' : AnalysisMethod(guenzel_23_local_mda, 'Günzel 2023 (local MDA)', 'G23(L-MDA)'),
    'guenzel23_l_mrda' : AnalysisMethod(guenzel_23_local_mrda, 'Günzel 2023 (local MRDA)', 'G23(L-MRDA)'),
    'guenzel23_inter' : AnalysisMethod(guenzel_23_inter, 'Günzel 2023 (inter)', 'G23(I)'),                      # TODO
    'hamann17' : AnalysisMethod(hamann17, 'Hamann 2017 (baseline)', 'H17'),
    'becker17' : None,                                                                                          # TODO
    'kordon20' : None,                                                                                          # TODO
    'martinez20_let' : None,                                                                                    # TODO
    'guenzel23_mixed' : AnalysisMethod(guenzel_23_mixed, 'Günzel 2023 (mixed)', 'G23(MIX)')                     # TODO
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
            [sg.Checkbox('Semi-harmonic periods', default=True, k='-Semi_harmonic_Box-', pad=((30,0),(0,0)), disabled=True)],
            [sg.Text('Min number Tasks:', pad=((35,0),(0,0))), sg.Input(s=5, k='-MINT_Input-', disabled=True, default_text='40'), sg.Text('Max number Tasks:'), sg.Input(s=5, k='-MAXT_Input-', disabled=True, default_text='60')],
            [sg.Text('Min Period:', pad=((35,0),(0,0))), sg.Input(s=10, k='-PMIN_Input-', disabled=True, default_text='1'), sg.Text('Max Period:'), sg.Input(s=10, k='-PMAX_Input-', disabled=True, default_text='2000')],
        [sg.Text('Target Utilization:'), sg.Spin(values=[i for i in range(0, 101)], initial_value=50, key='-Utilization_Spin-', s=(5,1))],
        [sg.Text('Number of Tasksets:'), sg.Input(s=10, k='-Number_Tasksets_Input-', default_text='1')],
    ], expand_x=True)]

    layoutChain = [sg.Frame('Cause-Effect Chain Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioChain", default=True, k='-Automotive_CEC_Radio-')],
        [sg.Radio('Random CECs', "RadioChain", default=False, k='-Random_CEC_Radio-')],
        [sg.Text('Min Chains:'), sg.Input(s=5, k='-Number_Chains_Min_Input-', default_text='30'), sg.Text('Max Chains:'), sg.Input(s=5, k='-Number_Chains_Max_Input-', default_text='60')]
    ], expand_x=True)]

    layoutAnalysis = [sg.Frame('Analysis Configuration', [
        [sg.TabGroup([[
            sg.Tab('Implicit Communication',[[sg.Column([
                [sg.Checkbox('Davare 2007 (baseline)', default=False, k='davare07')],
                [sg.Checkbox('Becker 2016', default=False, k='becker16')],
                [sg.Checkbox('Kloda 2018', default=False, k='kloda18')],
                [sg.Checkbox('Dürr 2019 (MRT)', default=False, k='duerr19_mrt')],
                [sg.Checkbox('Dürr 2019 (MRDA)', default=False, k='duerr19_mrda')],
                [sg.Checkbox('Martinez 2020', default=False, k='martinez20_impl')],
                [sg.Checkbox('Bi 2022', default=False, k='bi22')],
                [sg.Checkbox('Günzel 2023 (local MRT)', default=False, k='guenzel23_l_mrt')],
                [sg.Checkbox('Günzel 2023 (local MDA)', default=False, k='guenzel23_l_mda')],
                [sg.Checkbox('Günzel 2023 (local MRDA)', default=False, k='guenzel23_l_mrda')],
                [sg.Checkbox('Günzel 2023 (inter)', default=False, k='guenzel23_inter')]
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]), 
            sg.Tab('LET Communication', [[sg.Column([
                [sg.Checkbox('Hamann 2017 (baseline)', default=False, k='hamann17')],
                [sg.Checkbox('Becker 2017', default=False, k='becker17')],
                [sg.Checkbox('Kordon 2020', default=False, k='kordon20')],
                [sg.Checkbox('Martinez 2020', default=False, k='martinez20_let')],
                [sg.Checkbox('Günzel 2023 (mixed)', default=False, k='guenzel23_mixed')],
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]])
        ]], expand_x=True),
        sg.TabGroup([[
            sg.Tab('Implicit Communication',[[sg.Column([
                [sg.Checkbox('Davare 2007 (baseline)', default=True, k='n_davare07')],
                [sg.Checkbox('Becker 2016', default=False, k='n_becker16')],
                [sg.Checkbox('Kloda 2018', default=False, k='n_kloda18')],
                [sg.Checkbox('Dürr 2019 (MRT)', default=False, k='n_duerr19_mrt')],
                [sg.Checkbox('Dürr 2019 (MRDA)', default=False, k='n_duerr19_mrda')],
                [sg.Checkbox('Martinez 2020', default=False, k='n_martinez20_impl')],
                [sg.Checkbox('Bi 2022', default=False, k='n_bi22')],
                [sg.Checkbox('Günzel 2023 (local MRT)', default=False, k='n_guenzel23_l_mrt')],
                [sg.Checkbox('Günzel 2023 (local MDA)', default=False, k='n_guenzel23_l_mda')],
                [sg.Checkbox('Günzel 2023 (local MRDA)', default=False, k='n_guenzel23_l_mrda')],
                [sg.Checkbox('Günzel 2023 (inter)', default=False, k='n_guenzel23_inter')]
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]), 
            sg.Tab('LET Communication', [[sg.Column([
                [sg.Checkbox('Hamann 2017 (baseline)', default=False, k='n_hamann17')],
                [sg.Checkbox('Becker 2017', default=False, k='n_becker17')],
                [sg.Checkbox('Kordon 2020', default=False, k='n_kordon20')],
                [sg.Checkbox('Martinez 2020', default=False, k='n_martinez20_let')],
                [sg.Checkbox('Günzel 2023 (mixed)', default=False, k='n_guenzel23_mixed')],
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]])
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
        window['-Automotive_CEC_Radio-'].update(disabled=False)
        window['-Random_CEC_Radio-'].update(disabled=False)
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
                        cause_effect_chains += automotiveBench.gen_ce_chains(taskset, min_number_of_chains, max_number_of_chains)

                if generate_random_cecs:
                    # TODO
                    ...

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

