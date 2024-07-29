from framework import *
import getopt

def replace_value(dict, key, new_value):
    old_value = dict[key]
    if new_value == '':
        dict[key] = True
        return
    if isinstance(old_value, int):
        dict[key] = int(new_value)
        return
    if isinstance(old_value, float):
        dict[key] = float(new_value)
        return
    raise ValueError('Could not parse value for', key)


def analyze_cecs(cecs_file_path,
                 selected_analysis_methods,
                 selected_normalization_methods,
                 number_of_threads,
                 normalized_plots,
                 absolute_plots,
                 raw_analyses_results,
                 print_to_console):
    
    output_dir = helpers.make_output_directory()

    #############################
    ### Load Chains from file ###
    #############################

    cause_effect_chains = helpers.load_data(cecs_file_path)

    check_methods_and_cecs(
        selected_analysis_methods,
        selected_normalization_methods,
        cause_effect_chains
    )

    ####################
    ### Run Analyses ###
    ####################

    performAnalyses(
        cause_effect_chains, 
        selected_analysis_methods + selected_normalization_methods, 
        number_of_threads
    )


    #############################
    ### Generate output plots ###
    #############################

    if normalized_plots:
        create_normalized_plots(
            selected_analysis_methods, 
            selected_normalization_methods, 
            output_dir
        )

    if absolute_plots:
        create_absolute_plots(
            selected_analysis_methods, 
            output_dir
        )

    if raw_analyses_results:
        save_raw_analysis_results(
            selected_analysis_methods,
            selected_normalization_methods,
            output_dir
        )

    if print_to_console:
        for analysis_method in selected_analysis_methods:
            print(analysis_method.latencies)

    return output_dir


def runCLIMode(args):

    # cli mode has two options:
    # 1. create cause-effect chains and store them in a file
    # 2. load cause-effect chains from a file and analyse them

    debug_output = False

    ##################
    #### Read args ###
    ##################

    if args[0] == 'generate-cecs':

        number_of_threads = 1
        output_dir = ''

        # get default parameters
        taskset_generation_params = dict(default_taskset_generation_params)
        cec_generation_params = dict(default_cec_generation_params)

        taskset_generation_params['use_automotive_taskset_generation'] = False
        taskset_generation_params['use_semi_harmonic_periods'] = False
        cec_generation_params['generate_automotive_cecs'] = False

        options, arguments = getopt.getopt(
            args[1:],
            "t:o:",
            [param + '=' for param in list(taskset_generation_params.keys()) if not isinstance(taskset_generation_params[param], bool)] + 
            [param for param in list(taskset_generation_params.keys()) if isinstance(taskset_generation_params[param], bool)] +
            [param + '=' for param in list(cec_generation_params.keys()) if not isinstance(cec_generation_params[param], bool)] + 
            [param for param in list(cec_generation_params.keys()) if isinstance(cec_generation_params[param], bool)] + 
            ['debug']
        )

        for option, value in options:
            option = option.replace('-', '')
            if option in taskset_generation_params.keys():
                replace_value(taskset_generation_params, option, value)
            if option in cec_generation_params.keys():
                replace_value(cec_generation_params, option, value)
            if option == 't':
                number_of_threads = int(value)
            if option == 'o':
                output_dir = value
            if option == 'debug':
                debug_output = True

        if output_dir == '':
            output_dir = helpers.make_output_directory()

        # Debug Output

        if debug_output:
            print('[Info] number_of_threads:', number_of_threads)
            print('[Info] output_dir:', output_dir)
            print('[Info] taskset_generation_params:', taskset_generation_params)
            print('[Info] cec_generation_params:',cec_generation_params)


        check_params(
            taskset_generation_params,
            cec_generation_params,
            True
        )

        generate_cecs(
            taskset_generation_params,
            cec_generation_params,
            number_of_threads,
            True,
            output_dir
        )

    elif args[0] == 'analyze-cecs':

        selected_analysis_methods = []
        selected_normalization_methods = []
        cecs_file_path = ''
        number_of_threads = 1
        normalized_plots = False
        absolute_plots = False
        raw_analyses_results = False

        i = 1
        while i < len(args):

            if args[i] == '--normalized-plots':
                normalized_plots = True
                i+=1
                continue

            if args[i] == '--absolute-plots':
                absolute_plots = True
                i+=1
                continue

            if args[i] == '--csv-export':
                raw_analyses_results = True
                i+=1
                continue

            if args[i] == '--debug':
                debug_output = True
                i+=1
                continue

            if args[i] == '-a':
                # add analysis method
                if i+1 == len(args):
                    print("[ERROR] Missing argument after flag:", args[i])
                    print("[ERROR] Terminating")
                    return
                selected_analysis_methods.append(analysesDict[args[i+1]])
                i+=2
            elif args[i] == '-n':
                # add normalization method
                if i+1 == len(args):
                    print("[ERROR] Missing argument after flag:", args[i])
                    print("[ERROR] Terminating")
                    return
                selected_normalization_methods.append(analysesDict[args[i+1]])
                i+=2
            elif args[i] == '-f':
                # use specified file
                if i+1 == len(args):
                    print("[ERROR] Missing argument after flag:", args[i])
                    print("[ERROR] Terminating")
                    return
                cecs_file_path = args[i+1]
                i+=2
            elif args[i] == '-t':
                # use specified file
                if i+1 == len(args):
                    print("[ERROR] Missing argument after flag:", args[i])
                    print("[ERROR] Terminating")
                    return
                number_of_threads = int(args[i+1])
                i+=2
            else:
                # unknown option
                print("[ERROR] Passed unknown option:", args[i])
                print("[ERROR] Terminating")
                return

        if debug_output:
            print('[Info] Selected analysis methods:', selected_analysis_methods)
            print('[Info] Selected normalization methods:', selected_normalization_methods)
            print('[Info] Selected file:', cecs_file_path)
            print('[Info] Number of threads:', number_of_threads)
            print('[Info] Normalized plots:', normalized_plots)
            print('[Info] Absolute plots:', absolute_plots)
            print('[Info] CSV exports:', raw_analyses_results)

        output_dir = analyze_cecs(
            cecs_file_path,
            selected_analysis_methods,
            selected_normalization_methods,
            number_of_threads,
            normalized_plots,
            absolute_plots,
            raw_analyses_results,
            False
        )

        print('[Info] Run finished without any errors')
        print('[Info] Results are saved in:', output_dir)

    elif len(args) == 2:
        # simplest mode
        # first argument is the analysis method
        # second argument is the file to analyze
        selected_analysis_methods = [analysesDict[args[0]]]
        cecs_file_path = args[1]
        number_of_threads = 1

        output_dir = analyze_cecs(
            cecs_file_path,
            selected_analysis_methods,
            [],
            number_of_threads,
            False,
            False,
            False,
            True
        )

    elif len(args) == 3:
        # first argument is the analysis method
        # second argument is the file to analyze
        # third argument is the number of threads
        selected_analysis_methods = [analysesDict[args[0]]]
        cecs_file_path = args[1]
        number_of_threads = int(args[2])

        output_dir = analyze_cecs(
            cecs_file_path,
            selected_analysis_methods,
            [],
            number_of_threads,
            False,
            False,
            False,
            True
        )

    else:
        print('[ERROR] Could not parse input parameters')
        



