from framework import *


def generate_cecs():
    ######################
    ### Create Taskset ###
    ######################

    output_dir = helpers.make_output_directory()

    # first create a taskset

    # # selected automotive benchmark
    # if use_automotive_taskset:                        
    #     tasksets = generate_automotive_tasksets(
    #         target_utilization, 
    #         number_of_tasksets, 
    #         number_of_threads
    #     )

    # # selected uniform benchmark
    # if use_uniform_taskset_generation:
    #     tasksets = generate_uniform_tasksets(
    #         target_utilization, 
    #         min_number_of_tasks, 
    #         max_number_of_tasks, 
    #         min_period, 
    #         max_period, 
    #         use_semi_harmonic_periods,
    #         number_of_tasksets,
    #         number_of_threads
    #     )

    # for taskset in tasksets:
    #     adjust_taskset_release_pattern(taskset, sporadic_ratio)
    #     adjust_taskset_communication_policy(taskset, let_ratio)
    #     taskset.rate_monotonic_scheduling()
    #     taskset.compute_wcrts()

    # # remove tasksets with tasks that miss their deadline
    # tasksets = remove_invalid_tasksets(tasksets)


    #########################################
    ### Generate/Load Cause Effect Chains ###
    #########################################

    cause_effect_chains = []

    # if generate_automotive_cecs:
    #     cause_effect_chains = generate_automotive_cecs(
    #         tasksets, 
    #         min_number_of_chains, 
    #         max_number_of_chains
    #     )

    # if generate_random_cecs:
    #     cause_effect_chains = generate_random_cecs(
    #         tasksets, 
    #         min_number_tasks_in_chain, 
    #         max_number_tasks_in_chain, 
    #         min_number_of_chains, 
    #         max_number_of_chains
    #     )

    # if generate_interconnected_cecs:
    #     cause_effect_chains = create_interconnected_cecs(
    #         cause_effect_chains, 
    #         min_number_ecus, 
    #         max_number_ecus, 
    #         number_of_inter_cecs
    #     )

    # if store_generated_cecs:
    #     helpers.write_data(output_dir + "cause_effect_chains.pickle", cause_effect_chains)

    return cause_effect_chains


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
        ...
        # TODO
        generate_cecs()

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

        # check if given parameters are valid
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



