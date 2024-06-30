from framework import *


def analyze_cecs(cecs_file_path,
                 selected_analysis_methods,
                 selected_normalization_methods,
                 number_of_threads,
                 normalized_plots,
                 absolute_plots,
                 raw_analyses_results):
    
    output_dir = helpers.make_output_directory()

    #############################
    ### Load Chains from file ###
    #############################

    cause_effect_chains = helpers.load_data(cecs_file_path)

    print(len(cause_effect_chains))

    
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

    return output_dir


def runCLIMode(args):

    # cli mode has two options:
    # 1. create cause-effect chains and store them in a file
    # 2. load cause-effect chains from a file and analyse them

    ##################
    #### Read args ###
    ##################

    if args[0] == 'generate-cecs':

        number_of_threads = 1
        output_dir = ''

        # parameters for taskset generation
        taskset_generation_params = dict(default_taskset_generation_params)

        # parameters for cec generation
        cec_generation_params = dict(default_cec_generation_params)


        # TODO

        print('[Info] number_of_threads:', number_of_threads, '(default: 1)')

        # check if given arguments are valid
        # TODO

        if output_dir == '':
            output_dir = helpers.make_output_directory()

        generate_cecs(
            taskset_generation_params,
            cec_generation_params,
            number_of_threads,
            output_dir
        )

    if args[0] == 'analyze-cecs':

        selected_analysis_methods = []
        selected_normalization_methods = []
        cecs_file_path = ''
        number_of_threads = 1
        normalized_plots = False
        absolute_plots = False
        raw_analyses_results = False

        i = 1
        print(len(args))
        while i < len(args):
            print(i)

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

        print('[Info] Selected analysis methods:', selected_analysis_methods)
        print('[Info] Selected normalization methods:', selected_normalization_methods)
        print('[Info] Selected file:', cecs_file_path)
        print('[Info] Number of threads:', number_of_threads)

        # check if given arguments are valid
        # TODO

        output_dir = analyze_cecs(
            cecs_file_path,
            selected_analysis_methods,
            selected_normalization_methods,
            number_of_threads,
            normalized_plots,
            absolute_plots,
            raw_analyses_results
        )

        print('[Info] Run finished without any errors')
        print('[Info] Results are saved in:', output_dir)



