# E2EEvaluation
Evaluation Framework for End-to-End Analyses

## Installation
To use the evaluation framework, python3 is necessary. python3.10 was used during the development, but newer versions will likely work as well.
Additionally, the following commands can be executed to install the necessary software to run the framework (replace python3.X with the python version you are using):

- ```sudo apt install software-properties-common python3.X-venv python3.X-dev python3.X-tk git```

Then clone this repository and enter it:

- ```git clone https://github.com/tu-dortmund-ls12-rt/E2EEvaluation.git```
- ```cd E2EEvaluation```

Create a virtual environment to safely install python packages without dependency issues and activate it:

- ```python3.11 -m venv e2eEval```
- ```. e2eEval/bin/activate```

Install the python packages necessary to launch the evaluation framework. All of the necessary packages are specified in the requirements.txt, which can be automatically loaded and installed using the following command:

- ```pip install -r requirements.txt```

Otherwise the required python packages can also be installed manually using the following commands:

- ```pip install scipy numpy matplotlib```
- ```pip install pySimpleGUI/PySimpleGUI-4.60.5.tar.gz```
- ```pip install git+https://github.com/JasonGross/tikzplotlib.git```

## Running the Framework

The Framework offers a graphical user interface as well as a command line interface that can be used to configure an evaluation.

### Graphical User Interface

To start the graphical user interface, the following command can be used (active environment with installed python packages necessary):

- ```python3.X e2eMain.py```

### Command Line Interface

TODO

## Analyses Overview
List of papers with analyses methods relevant for the framework:

| Paper Title                                                                            | Short Name   | Periodic | Sporadic | Implicit | LET   | Result       | Status     |
|----------------------------------------------------------------------------------------|--------------|----------|----------|----------|-------|--------------|------------|
|Period Optimization for Hard Real-time Distributed Automotive Systems                   |Davare 2007   | Yes      | (Yes)    | Yes      | No    | MRT          | Integrated |
|Synthesizing Job-Level Dependencies for Automotive Multi-rate Effect Chains             |Becker 2016   | Yes      | No       | Yes      | No    | MRDA         | Integrated |
|End-to-end timing analysis of cause-effect chains in automotive embedded systems        |Becker 2017   | Yes      | No       | Yes      | Yes   | MRDA         | Integrated |
|Communication Centric Design in Complex Automotive Embedded Systems                     |Hamann 2017   | Yes      | Yes      | No       | Yes   | MDA/MRT      | Integrated |
|Latency analysis for data chains of real-time periodic tasks                            |Kloda 2018    | Yes      | No       | Yes      | No    | MDA/MRT      | Integrated |
|End-to-End Timing Analysis of Sporadic Cause-Effect Chains in Distributed Systems       |Dürr 2019     | Yes      | Yes      | Yes      | (Yes) | MRDA,MDA/MRT | Integrated |
|Evaluation of the Age Latency of a Real-Time Communicating System using the LET paradigm|Kordon 2020   | Yes      | No       | No       | Yes   | MDA          | Requested  |
|End-to-end latency characterization of task communication models for automotive systems |Martinez 2020 | Yes      | No       | Yes      | Yes   | MDA/MRT      | Missing    |
|Efficient Maximum Data Age Analysis for Cause-Effect Chains in Automotive Systems       |Bi 2022       | Yes      | No       | Yes      | No    | MRDA         | Integrated |
|Data-Age Analysis for Multi-Rate Task Chains under Timing Uncertainty                   |Gohary 2022   | Yes      | No       | Yes      | No    | MRDA         | Integrated |
|Timing Analysis of Asynchronized Distributed Cause-Effect Chains                        |Günzel 2021   | Yes      | (Yes)    | Yes      | Yes   | MRDA,MDA/MRT | Integrated |
|Timing Analysis of Cause-Effect Chains with Heterogeneous Communication Mechanisms      |Günzel 2023   | Yes      | Yes      | Yes      | Yes   | MRT          | Integrated |
|Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains          |Günzel 2023   | Yes      | (Yes)    | Yes      | Yes   | MRDA,MDA/MRT | Integrated |
|On the Equivalence of Maximum Reaction Time and Maximum Data Age for Cause-Effect Chains|Günzel 2023   | Yes      | (Yes)    | (Yes)    | Yes   | MDA/MRT      | Integrated |
|                                                                                        |              |          |          |          |       |              |            |
|Characterizing the Effect of Deadline Misses on Time-Triggered Task Chains              |Pazzaglia 2022| Yes      | No       | No       | Yes   | ?            | Received   |
|                                                                                        |              |          |          |          |       |              |            |
|End-To-End Timing Analysis in ROS2                                                      |Teper 2022    | ?        | ?        | ?        | ?     | ?            | Missing    |
|Latency analysis of self-suspending task chains                                         |Kloda 2022    | Yes      | No       | Yes      | No    | MRT          | Missing    |
|Reaction Time Analysis of Event-Triggered Processing Chains with Data Refreshing        |Tang 2023     | Yes      | No       | Yes      | No    | ?            | Missing    |

## File structure

    .
    ├── benchmarks				        # Folder with all available benchmarks
    │	├── benchmark_Uniform.py		# Uniform taskset/cec generation
    │	└── benchmark_WATERS.py		    # Automotive (WATERS) benchmark
    ├── cechains				
    │	├── chain.py			        # Definiton of a cause-effect chain
    │	└── jobchain.py			        # Definiton of a job-chain
    ├── e2eAnalyses				        # All analysis methods of the framework
    │	├── Becker2017.py
    │	├── BeckerFast.py
    │	├── Bi2022.py
    │	├── Davare2007.py
    │	├── Duerr2019.py
    │	├── Gohary2022.py
    │	├── Guenzel2023_equi.py
    │	├── Guenzel2023_equi_extension1.py
    │	├── Guenzel2023_equi_extension2.py
    │	├── Guenzel2023_inter.py
    │	├── Guenzel2023_mixed.py
    │	├── Hamann2017.py
    │	├── Kloda2018.py
    │	├── Kordon2020.py
    │	└── Martinez2020.py
    ├── external                        # Directory for loosely integrated analyses
    ├── output                          # Output directory with evaluation results
    ├── plotting
    │	└── plot.py				        # Methods for creating the box plots
    ├── pySimpleGUI
    │	└── PySimpleGUI-4.60.5.tar.gz   # Last free software version of PSG
    ├── tasks
    │	├── job.py				        # Definition of a job
    │	├── task.py				        # Definition of a task
    │	└── taskset.py			        # Definition of a taskset
    ├── utilities				        # Extra code, only necessary for some analyses
    │	├── analyzer_guenzel23.py
    │	├── analyzer.py
    │	├── augmented_job_chain.py
    │	├── csv_import_gohary.py
    │	├── event_simulator.py
    │	├── scheduler.py
    │	├── yaml_export_gohary.py
    │	└── yaml_export.py
    ├── .gitignore
    ├── consoleInterface.py			    # Parses the given console arguments
    ├── e2eMain.py				        # Main file to start the framework
    ├── framework.py				    # Logic of the framework
    ├── graphicalInterface.py			# Starts the GUI and collects input values
    ├── helpers.py				        # Helpers for file access
    ├── LICENSE
    ├── README.md
    └── requirements.txt
