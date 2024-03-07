import PySimpleGUI as sg

sg.theme('system default')


layoutGeneral = [sg.Frame('General Settings', [
    [sg.Radio('Generate Taskset', "RadioGeneral", default=True, k='-RG1-')],
        [sg.Checkbox('Store generated Taskset', default=False, k='-CBG1-', pad=((30,0),(0,0)))],
        [sg.Checkbox('Use custom seed', default=False, k='-CBG2-', pad=((30,0),(0,0))), sg.Input(s=20)],
        [sg.Checkbox('homogeneous', default=False, k='-CBG3-', pad=((30,0),(0,0)))],
    [sg.Radio('Load Taskset from File', "RadioGeneral", default=False, k='-RG2-')],
        [sg.Text('File:', pad=((35,0),(0,0))), sg.Input(s=50)],
])]

layoutTaskset = [sg.Frame('Taskset Configuration', [
    [sg.Radio('Automotive Benchmark', "RadioTaskset", default=True, k='-RT1-')],        #   U, #Tasksets?
    [sg.Radio('Uniform Taskset Generation', "RadioTaskset", default=False, k='-RT2-')], #   n, U*, #Tasksets?
])]

layoutChain = [sg.Frame('Cause-Effect Chain Configuration', [
    [sg.Radio('Automotive Benchmark', "RadioChain", default=True, k='-RC1-')],
])]

layoutAnalysis = [sg.Frame('Analysis Configuration', 
    [[sg.Text('Placeholder')]]
)]

layoutPlot = [sg.Frame('Plot Configuration', 
    [[sg.Text('Placeholder')]]
)]

layout = [
    [layoutGeneral],
    [layoutTaskset],
    [layoutChain],
    [layoutAnalysis],
    [layoutPlot],
    [sg.Button('OK'), sg.Button('Abbrechen')]
]

font = ("Arial", 11)
window = sg.Window('Evaluation Framework for End-to-End Analysis', layout, font=font)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Abbrechen':
        break
    elif event == 'OK':
        # do something
        print('OK')

window.close()
