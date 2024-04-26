import PySimpleGUI as sg
import benchmarks.benchmark_WATERS as automotiveBench
from e2eAnalyses.Davare2007 import davare07
from e2eAnalyses.Duerr2019 import duerr19, duerr_19_mrt, duerr_19_mrda
from e2eAnalyses.Hamann2017 import hamann17
from e2eAnalyses.Kloda2018 import kloda18
import helpers
import plotting.plot as p
import sys


analysesDict = {
    '-davare07-' : davare07,
    '-becker16-' : None,
    '-kloda18-' : kloda18,
    '-duerr19_mrt-' : duerr_19_mrt,
    '-duerr19_mrda-' : duerr_19_mrda,
    '-martinez20_impl-' : None,
    '-bi22-' : None,
    '-guenzel23_impl-' : None,
    '-hamann17-' : hamann17,
    '-becker17-' : None,
    '-kordon20-' : None,
    '-martinez20_let-' : None,
    '-guenzel23_let-' : None
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
            [sg.Text('Target Utilization:', pad=((35,0),(0,0))), sg.Slider(range=(0, 100), default_value=50, orientation='horizontal', key='-SL-', s=(20,10))],
            [sg.Text('Number of Tasksets:', pad=((35,0),(0,0))), sg.Input(s=10, k='-ANOT_Input-', default_text='1')],
        [sg.Radio('Uniform Taskset Generation (TODO)', "RadioTaskset", default=False, k='-RT2-', enable_events=True)], #   n, U*, #Tasksets?
    ], expand_x=True)]

    layoutChain = [sg.Frame('Cause-Effect Chain Configuration', [
        [sg.Radio('Automotive Benchmark', "RadioChain", default=True, k='-RC1-')],
    ], expand_x=True)]

    layoutAnalysis = [sg.Frame('Analysis Configuration', [
        [sg.TabGroup([[
            sg.Tab('Implicit Communication',[[sg.Column([
                [sg.Checkbox('Davare 2007 (baseline)', default=False, k='-davare07-')],
                [sg.Checkbox('Becker 2016', default=False, k='-becker16-')],
                [sg.Checkbox('Kloda 2018', default=False, k='-kloda18-')],
                [sg.Checkbox('Dürr 2019 (MRT)', default=False, k='-duerr19_mrt-')],
                [sg.Checkbox('Dürr 2019 (MRDA)', default=False, k='-duerr19_mrda-')],
                [sg.Checkbox('Martinez 2020', default=False, k='-martinez20_impl-')],
                [sg.Checkbox('Bi 2022', default=False, k='-bi22-')],
                [sg.Checkbox('Günzel 2023', default=False, k='-guenzel23_impl-')]
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]), 
            sg.Tab('LET Communication', [[sg.Column([
                [sg.Checkbox('Hamann 2017 (baseline)', default=False, k='-hamann17-')],
                [sg.Checkbox('Becker 2017', default=False, k='-becker17-')],
                [sg.Checkbox('Kordon 2020', default=False, k='-kordon20-')],
                [sg.Checkbox('Martinez 2020', default=False, k='-martinez20_let-')],
                [sg.Checkbox('Günzel 2023', default=False, k='-guenzel23_let-')],
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]])
        ]], expand_x=True)]
    ], expand_x=True)]

    layoutPlot = [sg.Frame('Plot Configuration', [
        [sg.Checkbox('create normalized plots (latency reduction compared to baseline)', default=True, k='-T1-')],
        [sg.Checkbox('create absolute plots', default=False, k='-T1-')],
        [sg.Checkbox('save raw analyses results', default=False, k='-T1-')]
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
        if values['-RT1-']:
            window['-SL-'].update(disabled=False)
            window['-ANOT_Input-'].update(disabled=False)

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

    if event == '-RT1-':
        window['-SL-'].update(disabled=False)
        window['-ANOT_Input-'].update(disabled=False)

    if event == '-RT2-':
        window['-SL-'].update(disabled=True)
        window['-ANOT_Input-'].update(disabled=True)


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
            target_utilization = values['-SL-']/100
            if use_automotive_taskset:
                try:
                    number_of_tasksets = int(values['-ANOT_Input-'])
                except ValueError:
                    popUp('ValueError', [f"Invalid number of tasksets '{values['-ANOT_Input-']}'!"])
                    continue
            use_uniform_taskset_generation = values['-RT2-']
            use_automotive_cause_effect_chain = values['-RC1-']
            
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
                    tasksets = []

                # store generated taskset
                if store_generated_taskset:
                    helpers.write_data(output_dir + "taskset.pickle", tasksets)

            # user selected load Taskset from file
            if load_taskset_from_file:
                tasksets = helpers.load_data(taskset_file_path)

            ####################################
            ### Generate Cause Effect Chains ###
            ####################################

            cause_effect_chains = []
            for taskset in tasksets:
                taskset.compute_wcrts()
                cause_effect_chains += automotiveBench.gen_ce_chains(taskset)

            ####################
            ### Run Analyses ###
            ####################

            latencies = performAnalyses(cause_effect_chains, selected_methods)
            print(latencies)

            #(
            result_baseline = []
            result_duerr = []

            result_duerr_mrt = []
            result_duerr_mrda = []

            result_kloda = []

            for cause_effect_chain in cause_effect_chains:
                result_baseline.append(davare07(cause_effect_chain))
                result_duerr.append(duerr19(cause_effect_chain))
                result_duerr_mrt.append(duerr_19_mrt(cause_effect_chain))
                result_duerr_mrda.append(duerr_19_mrda(cause_effect_chain))
                result_kloda.append(kloda18(cause_effect_chain))

            print('result_duerr')
            print(result_duerr)
            print('result_duerr_mrt')
            print(result_duerr_mrt)
            print('result_duerr_mrda')
            print(result_duerr_mrda)
            print('result_kloda')
            print(result_kloda)

            diff = [(b-a)/b for a,b in zip(result_duerr, result_baseline)]
            #)

            ########################
            ### Plot the results ###
            ########################

            # absolute plots
            for i in range(len(latencies)):
                if len(latencies[i]) > 0:
                    p.plot(latencies[i], output_dir + selected_methods[i].__name__ + ".pdf")

            #(
            p.plot(result_baseline, output_dir + "baseline.pdf")
            p.plot(result_duerr, output_dir + "duerr.pdf")
            p.plot(diff, output_dir + "duerr_precision_gain.pdf")
            #)

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

