import PySimpleGUI as sg
import benchmarks.benchmark_WATERS as automotiveBench
from e2eAnalyses.Davare2007 import davare07
from e2eAnalyses.Duerr2019 import duerr19
from e2eAnalyses.Hamann2017 import hamann17
import helpers
import plotting.plot as p
import sys


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
                [sg.Checkbox('Dürr 2019', default=False, k='-duerr19-')],
                [sg.Checkbox('Martinez 2020', default=False, k='-martinez20-')],
                [sg.Checkbox('Bi 2022', default=False, k='-bi22-')],
                [sg.Checkbox('Günzel 2023', default=False, k='-guenzel23-')]
            ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]), 
            sg.Tab('LET Communication', [[sg.Column([
                [sg.Checkbox('Hamann 2017 (baseline)', default=False, k='-hamann17-')],
                [sg.Checkbox('Becker 2017', default=False, k='-becker17-')],
                [sg.Checkbox('Kordon 2020', default=False, k='-kordon20-')],
                [sg.Checkbox('Martinez 2020', default=False, k='-martinez20-')],
                [sg.Checkbox('Günzel 2023', default=False, k='-guenzel23-')],
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


def performAnalyses(cec, methods):
    #TODO
    return 0


if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) == 0:
        print("User did not pass any arguments (launching visual-mode)")
        #TODO

    if len(args) > 0:
        print("User specified following arguments (launching CLI-mode):")
        print(args)
        #TODO: check if args are valid
        #TODO: launch cli-mode

    window = inititalizeUI()

    while True:
        event, values = window.read()
        updateUI(window, event, values)

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        if event == 'Run':

            ##########################################
            ### Check whether all inputs are valid ###
            ##########################################

            print(values)
            #TODO

            ###########################
            ### Create/Load Taskset ###
            ###########################

            output_dir = helpers.make_output_directory()

            # user selected generate Taskset
            if values['-RG1-']:
                
                # selected automotive benchmark
                if values['-RT1-']:
                    target_utilization = values['-SL-']/100

                    try:
                        number_of_tasksets = int(values['-ANOT_Input-'])
                    except ValueError:
                        popUp('ValueError', [f"Invalid number of tasksets '{values['-ANOT_Input-']}'!"])
                        continue
                        
                    tasksets = [automotiveBench.gen_taskset(target_utilization) for _ in range(number_of_tasksets)]

                # selected uniform benchmark
                else:
                    tasksets = []

                # store generated taskset
                if values['-CB1-']:
                    helpers.write_data(output_dir + "taskset.pickle", tasksets)

            # user selected load Taskset from file
            if values['-RG2-']:
                tasksets = helpers.load_data(values['-F_Input-'])

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

            result_baseline = []
            result_duerr = []

            for cause_effect_chain in cause_effect_chains:
                result_baseline.append(davare07(cause_effect_chain))
                result_duerr.append(duerr19(cause_effect_chain))

            diff = [(b-a)/b for a,b in zip(result_duerr, result_baseline)]

            ########################
            ### Plot the results ###
            ########################

            p.plot(result_baseline, output_dir + "baseline.pdf")
            p.plot(result_duerr, output_dir + "duerr.pdf")
            p.plot(diff, output_dir + "duerr_precision_gain.pdf")

            #######################
            ### Feedback pop-up ###
            #######################

            popUp('Info', 
                ['Run finished without any errors.', 
                'Results are saved in:', 
                output_dir]
            )


    window.close()
