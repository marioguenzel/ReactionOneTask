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
import plotting.plot as p
import sys


analysesDict = {
    '-davare07-' : davare07,
    '-becker16-' : None,                            # TODO
    '-kloda18-' : kloda18,
    '-duerr19_mrt-' : duerr_19_mrt,
    '-duerr19_mrda-' : duerr_19_mrda,
    '-martinez20_impl-' : None,                     # TODO
    '-bi22-' : None,                                # TODO
    '-guenzel23_l_mrt-' : guenzel_23_local_mrt,
    '-guenzel23_l_mda-' : guenzel_23_local_mda,
    '-guenzel23_l_mrda-' : guenzel_23_local_mrda,
    '-guenzel23_inter-' : guenzel_23_inter,         # TODO
    '-hamann17-' : hamann17,
    '-becker17-' : None,                            # TODO
    '-kordon20-' : None,                            # TODO
    '-martinez20_let-' : None,                      # TODO
    '-guenzel23_mixed-' : guenzel_23_mixed          # TODO
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
        [sg.Radio('Generate Taskset', "RadioGeneral", default=True, k='-RG1-', enable_events=True)],
            [sg.Checkbox('Store generated Taskset', default=False, k='-CB1-', pad=((30,0),(0,0)))],
            [sg.Checkbox('Use custom seed', default=False, k='-CB2-', pad=((30,0),(0,0))), sg.Input(s=20, k='-Seed-')],
        [sg.Radio('Load Taskset from File', "RadioGeneral", default=False, k='-RG2-', enable_events=True)],
            [sg.Text('File:', pad=((35,0),(0,0))), sg.Input(s=50, k='-F_Input-', disabled=True), sg.FileBrowse(file_types=(("Taskset File", "*.pickle"),), k="-Browse-", disabled=True)],
    ], expand_x=True)]

    layoutTaskset = [sg.Frame('Taskset Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioTaskset", default=True, k='-RT1-', enable_events=True)],        #   U, #Tasksets?
        [sg.Radio('Uniform Taskset Generation', "RadioTaskset", default=False, k='-RT2-', enable_events=True)], #   n, U*, #Tasksets?
            [sg.Checkbox('Semi-harmonic periods', default=True, k='-CBT1-', pad=((30,0),(0,0)), disabled=True)],
            [sg.Text('Min number Tasks:', pad=((35,0),(0,0))), sg.Input(s=10, k='-MINT_Input-', disabled=True, default_text='40'), sg.Text('Max number Tasks:'), sg.Input(s=10, k='-MAXT_Input-', disabled=True, default_text='60')],
            [sg.Text('Min Period:', pad=((35,0),(0,0))), sg.Input(s=10, k='-PMIN_Input-', disabled=True, default_text='1'), sg.Text('Max Period:'), sg.Input(s=10, k='-PMAX_Input-', disabled=True, default_text='2000')],
        [sg.Text('Target Utilization:'), sg.Slider(range=(0, 100), default_value=50, orientation='horizontal', key='-SL-', s=(20,10))],
        [sg.Text('Number of Tasksets:'), sg.Input(s=10, k='-ANOT_Input-', default_text='1')],
    ], expand_x=True)]

    layoutChain = [sg.Frame('Cause-Effect Chain Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioChain", default=True, k='-RC1-')],
    ], expand_x=True)]

    layoutAnalysis = [sg.Frame('Analysis Configuration', [
        [sg.TabGroup([[
            sg.Tab('Implicit Communication',[[sg.Column([
                [sg.Checkbox('Davare 2007 (baseline)', default=True, k='-davare07-', disabled=True)],
                [sg.Checkbox('Becker 2016', default=False, k='-becker16-')],
                [sg.Checkbox('Kloda 2018', default=False, k='-kloda18-')],
                [sg.Checkbox('Dürr 2019 (MRT)', default=False, k='-duerr19_mrt-')],
                [sg.Checkbox('Dürr 2019 (MRDA)', default=False, k='-duerr19_mrda-')],
                [sg.Checkbox('Martinez 2020', default=False, k='-martinez20_impl-')],
                [sg.Checkbox('Bi 2022', default=False, k='-bi22-')],
                [sg.Checkbox('Günzel 2023 (local MRT)', default=False, k='-guenzel23_l_mrt-')],
                [sg.Checkbox('Günzel 2023 (local MDA)', default=False, k='-guenzel23_l_mda-')],
                [sg.Checkbox('Günzel 2023 (local MRDA)', default=False, k='-guenzel23_l_mrda-')],
                [sg.Checkbox('Günzel 2023 (inter)', default=False, k='-guenzel23_inter-')]
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]), 
            sg.Tab('LET Communication', [[sg.Column([
                [sg.Checkbox('Hamann 2017 (baseline)', default=False, k='-hamann17-')],
                [sg.Checkbox('Becker 2017', default=False, k='-becker17-')],
                [sg.Checkbox('Kordon 2020', default=False, k='-kordon20-')],
                [sg.Checkbox('Martinez 2020', default=False, k='-martinez20_let-')],
                [sg.Checkbox('Günzel 2023 (mixed)', default=False, k='-guenzel23_mixed-')],
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]])
        ]], expand_x=True)]
    ], expand_x=True)]

    layoutPlot = [sg.Frame('Plot Configuration', [
        [sg.Checkbox('create normalized plots (latency reduction compared to baseline)', default=True, k='-CBP1-')],
        [sg.Checkbox('create absolute plots', default=False, k='-CBP2-')],
        [sg.Checkbox('save raw analyses results', default=False, k='-CBP3-')]
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
    if event == '-RG1-':
        window['-CB1-'].update(disabled=False)
        window['-CB2-'].update(disabled=False)
        window['-Seed-'].update(disabled=False)
        window['-F_Input-'].update(disabled=True)
        window['-Browse-'].update(disabled=True)
        window['-RT1-'].update(disabled=False)
        window['-RT2-'].update(disabled=False)
        window['-SL-'].update(disabled=False)
        window['-ANOT_Input-'].update(disabled=False)
        if values['-RT2-']:
            window['-CBT1-'].update(disabled=False)
            window['-MINT_Input-'].update(disabled=False)
            window['-MAXT_Input-'].update(disabled=False)
            window['-PMIN_Input-'].update(disabled=False)
            window['-PMAX_Input-'].update(disabled=False)

    if event == '-RG2-':
        window['-CB1-'].update(disabled=True)
        window['-CB2-'].update(disabled=True)
        window['-Seed-'].update(disabled=True)
        window['-F_Input-'].update(disabled=False)
        window['-Browse-'].update(disabled=False)
        window['-RT1-'].update(disabled=True)
        window['-RT2-'].update(disabled=True)
        window['-SL-'].update(disabled=True)
        window['-ANOT_Input-'].update(disabled=True)
        window['-CBT1-'].update(disabled=True)
        window['-MINT_Input-'].update(disabled=True)
        window['-MAXT_Input-'].update(disabled=True)
        window['-PMIN_Input-'].update(disabled=True)
        window['-PMAX_Input-'].update(disabled=True)

    if event == '-RT1-':
        window['-CBT1-'].update(disabled=True)
        window['-MINT_Input-'].update(disabled=True)
        window['-MAXT_Input-'].update(disabled=True)
        window['-PMIN_Input-'].update(disabled=True)
        window['-PMAX_Input-'].update(disabled=True)

    if event == '-RT2-':
        window['-CBT1-'].update(disabled=False)
        window['-MINT_Input-'].update(disabled=False)
        window['-MAXT_Input-'].update(disabled=False)
        window['-PMIN_Input-'].update(disabled=False)
        window['-PMAX_Input-'].update(disabled=False)



def normalizeLatencies(toNormalize, baseline):
    return [(b-a)/b for a,b in zip(toNormalize, baseline)]


def performAnalyses(cause_effect_chains, methods):
    latencies_all = []
    
    for method in methods:
        if method == None:
            latencies_all.append([])
            continue
        
        latencies_single = []
        for cause_effect_chain in cause_effect_chains:
            latencies_single.append(method(cause_effect_chain))
        
        latencies_all.append(latencies_single)

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

            generate_taskset = values['-RG1-']
            store_generated_taskset = values['-CB1-']
            use_custom_seed = values['-CB2-']
            if generate_taskset and use_custom_seed:
                try:
                    custom_seed = int(values['-Seed-'])
                except ValueError:
                    popUp('ValueError', [f"Invalid seed '{values['-Seed-']}'!"])
                    continue
            load_taskset_from_file = values['-RG2-']
            taskset_file_path = values['-F_Input-']
            use_automotive_taskset = values['-RT1-']
            use_uniform_taskset_generation = values['-RT2-']
            target_utilization = values['-SL-']/100
            try:
                number_of_tasksets = int(values['-ANOT_Input-'])
            except ValueError:
                popUp('ValueError', [f"Invalid number of tasksets '{values['-ANOT_Input-']}'!"])
                continue
            use_semi_harmonic_periods = values['-CBT1-']
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

            use_automotive_cause_effect_chain = values['-RC1-']
            create_normalized_plots = values['-CBP1-']
            create_absolute_plots = values['-CBP2-']
            save_raw_analyses_results = values['-CBP3-']
            
            selected_methods = []
            for key in analysesDict.keys():
                if values[key] == True:
                    selected_methods.append(analysesDict[key])

            print(values)
            print(selected_methods)

            ##########################################
            ### Check whether all inputs are valid ###
            ##########################################

            #TODO

            ###########################
            ### Create/Load Taskset ###
            ###########################

            output_dir = helpers.make_output_directory()

            # user selected generate Taskset
            if generate_taskset:
                
                # selected automotive benchmark
                if use_automotive_taskset:                        
                    tasksets = [automotiveBench.gen_taskset(target_utilization) for _ in range(number_of_tasksets)]

                # selected uniform benchmark
                if use_uniform_taskset_generation:
                    tasksets = [uniformBench.gen_taskset(
                        target_utilization, 
                        min_number_of_tasks, 
                        max_number_of_tasks,
                        min_period,
                        max_period,
                        use_semi_harmonic_periods,
                        False
                        )
                    for _ in range(number_of_tasksets)]

                # store generated taskset
                if store_generated_taskset:
                    helpers.write_data(output_dir + "taskset.pickle", tasksets)

            # user selected load Taskset from file
            if load_taskset_from_file:
                tasksets = helpers.load_data(taskset_file_path)

            for taskset in tasksets:
                taskset.rate_monotonic_scheduling()
                taskset.compute_wcrts()
                taskset.print_tasks()
                taskset.print()


            # remove tasksets with tasks that miss their deadline
            valid_tasksets = tasksets.copy()
            for taskset in tasksets:
                for task in taskset:
                    if taskset.wcrts[task] > task.deadline:
                        valid_tasksets.remove(taskset)
                        break
            tasksets = valid_tasksets

            ####################################
            ### Generate Cause Effect Chains ###
            ####################################

            cause_effect_chains = []
            for taskset in tasksets:
                cause_effect_chains += automotiveBench.gen_ce_chains(taskset)

            print(len(cause_effect_chains))

            ####################
            ### Run Analyses ###
            ####################

            latencies = performAnalyses(cause_effect_chains, selected_methods)

            ########################
            ### Plot the results ###
            ########################

            analyses_names = []
            for i in range(len(selected_methods)):
                analyses_names.append(selected_methods[i].__name__)
                print(analyses_names[i])
                print(latencies[i])

            # normalized plots
            normalized_latencies = []
            if create_normalized_plots:
                for i in range(1, len(latencies)):
                    if len(latencies[i]) > 0:
                        normalized_latencies.append(normalizeLatencies(latencies[i], latencies[0]))
                        p.plot(normalized_latencies[i-1], output_dir + analyses_names[i] + "_normalized.pdf", title=(analyses_names[i] + " (normalized)"))

                # only do comparison if there is something to compare
                if len(latencies) >= 3:
                    p.plot(normalized_latencies, output_dir + "normalized.pdf", xticks=analyses_names[1:], title="Normalized Comparison")

            # absolute plots
            if create_absolute_plots:
                for i in range(len(latencies)):
                    if len(latencies[i]) > 0:
                        p.plot(latencies[i], output_dir + analyses_names[i] + ".pdf")

                # only do comparison if there is something to compare
                if len(latencies) >= 3:
                    p.plot(latencies, output_dir + "absolute.pdf", xticks=analyses_names, title="Absolute Comparison")


            if save_raw_analyses_results:
                ...
                # TODO

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
        print("User did not pass any arguments (launching visual-mode)")
        window = inititalizeUI()
        runVisualMode(window)
        window.close()

    if len(args) > 0:
        print("User specified following arguments (launching CLI-mode):")
        print(args)
        #TODO: check if args are valid
        #TODO: launch cli-mode

