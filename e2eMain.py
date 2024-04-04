import PySimpleGUI as sg
import benchmarks.benchmark_WATERS as automotiveBench
from e2eAnalyses.Davare2007 import davare
import helpers

sg.theme('system default')

# Definition of the user interface layout

layoutMenu = [sg.Menu([['Help', ['Edit Me']], ['About', ['Edit Me']]],  k='-CUST MENUBAR-')]

layoutGeneral = [sg.Frame('General Settings', [
    [sg.Radio('Generate Taskset', "RadioGeneral", default=True, k='-RG1-', enable_events=True)],
        [sg.Checkbox('Store generated Taskset', default=False, k='-CB1-', pad=((30,0),(0,0)))],
        [sg.Checkbox('Use custom seed', default=False, k='-CB2-', pad=((30,0),(0,0))), sg.Input(s=20, k='-Seed-')],
        [sg.Checkbox('homogeneous', default=False, k='-CB3-', pad=((30,0),(0,0)))],
    [sg.Radio('Load Taskset from File', "RadioGeneral", default=False, k='-RG2-', enable_events=True)],
        [sg.Text('File:', pad=((35,0),(0,0))), sg.Input(s=50, k='-F_Input-', disabled=True), sg.FileBrowse(file_types=(("Taskset File", "*.pickle"),), k="-Browse-", disabled=True)],
], expand_x=True)]

layoutTaskset = [sg.Frame('Taskset Configuration', [
    [sg.Radio('Automotive Benchmark', "RadioTaskset", default=True, k='-RT1-')],        #   U, #Tasksets?
        [sg.Text('Target Utilization:', pad=((35,0),(0,0))), sg.Slider(range=(0, 100), default_value=50, orientation='horizontal', key='-SL-', s=(20,10))],
        [sg.Text('Number of Tasksets:', pad=((35,0),(0,0))), sg.Input(s=10, k='-ANOT_Input-')],
    [sg.Radio('Uniform Taskset Generation', "RadioTaskset", default=False, k='-RT2-')], #   n, U*, #Tasksets?
], expand_x=True)]

layoutChain = [sg.Frame('Cause-Effect Chain Configuration', [
    [sg.Radio('Automotive Benchmark', "RadioChain", default=True, k='-RC1-')],
], expand_x=True)]

layoutAnalysis = [sg.Frame('Analysis Configuration', [
    [sg.TabGroup([[
        sg.Tab('Implicit Com.',[[sg.Column([
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')]
        ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]]), 
        sg.Tab('LET Com.', [[sg.Column([
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')],
            [sg.Checkbox('Test', default=False, k='-T1-')]
        ], expand_x=True, expand_y=True, scrollable=True, vertical_scroll_only=True)]])
    ]], expand_x=True)]
], expand_x=True)]

layoutPlot = [sg.Frame('Plot Configuration', 
    [[sg.Text('Placeholder')]]
, expand_x=True, expand_y=True)]

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

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Cancel':
        break
    elif event == '-RG1-':
        window['-CB1-'].update(disabled=False)
        window['-CB2-'].update(disabled=False)
        window['-CB3-'].update(disabled=False)
        window['-Seed-'].update(disabled=False)
        window['-F_Input-'].update(disabled=True)
        window['-Browse-'].update(disabled=True)
        window['-RT1-'].update(disabled=False)
        window['-RT2-'].update(disabled=False)
        window['-RC1-'].update(disabled=False)
    elif event == '-RG2-':
        window['-CB1-'].update(disabled=True)
        window['-CB2-'].update(disabled=True)
        window['-CB3-'].update(disabled=True)
        window['-Seed-'].update(disabled=True)
        window['-F_Input-'].update(disabled=False)
        window['-Browse-'].update(disabled=False)
        window['-RT1-'].update(disabled=True)
        window['-RT2-'].update(disabled=True)
        window['-RC1-'].update(disabled=True)
    elif event == 'Run':

        ### Create/Load Taskset ###

        # user selected generate Taskset
        if values['-RG1-']:
            
            # selected automotive benchmark
            if values['-RT1-']:
                target_utilization = values['-SL-']/100
                number_of_tasksets = int(values['-ANOT_Input-'])
                tasksets = [automotiveBench.gen_taskset(target_utilization) for _ in range(number_of_tasksets)]

            # selected uniform benchmark
            else:
                tasksets = []

            # store generated taskset
            if values['-CB1-']:
                output_dir = helpers.check_or_make_output_directory("output/")
                helpers.write_data(output_dir + "taskset.pickle", tasksets)

        # user selected load Taskset from file
        if values['-RG2-']:
            tasksets = helpers.load_data(values['-F_Input-'])

        ### Generate Cause Effect Chains ###

        cause_effect_chains = []
        for taskset in tasksets:
            taskset.compute_wcrts()
            #taskset.print()
            #taskset.print_tasks()
            cause_effect_chains += automotiveBench.gen_ce_chains(taskset)

        ### Run Analyses ###

        res = []
        for cause_effect_chain in cause_effect_chains:
            res.append(davare(cause_effect_chain))

        print(res)

        ### Plot the results ###

        sg.Window('Info',
            [[sg.T('Run finished without any errors.')],
            [sg.Push(), sg.B('OK'), sg.Push()]]).read(close=True)


window.close()
