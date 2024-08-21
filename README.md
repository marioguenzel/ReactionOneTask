# E2EEvaluation
Evaluation Framework for End-to-End Analyses

## Required Packages
To install the necessary (python) packages run the following commands:

```
sudo apt-get install python3-tk
pip install pySimpleGUI/PySimpleGUI-4.60.5.tar.gz
pip install scipy numpy matplotlib
```
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
|End-to-end latency characterization of task communication models for automotive systems |Martinez 2020 | Yes      | No       | Yes      | Yes   | MDA/MRT      | Unavailable|
|Efficient Maximum Data Age Analysis for Cause-Effect Chains in Automotive Systems       |Bi 2022       | Yes      | No       | Yes      | No    | MRDA         | Integrated |
|Timing Analysis of Asynchronized Distributed Cause-Effect Chains                        |Günzel 2021   | Yes      | (Yes)    | Yes      | Yes   | MRDA,MDA/MRT | Integrated |
|Timing Analysis of Cause-Effect Chains with Heterogeneous Communication Mechanisms      |Günzel 2023   | Yes      | Yes      | Yes      | Yes   | MRT          | Integrated |
|Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains          |Günzel 2023   | Yes      | (Yes)    | Yes      | Yes   | MRDA,MDA/MRT | Integrated |
|On the Equivalence of Maximum Reaction Time and Maximum Data Age for Cause-Effect Chains|Günzel 2023   | Yes      | (Yes)    | (Yes)    | Yes   | MDA/MRT      | Integrated |
|                                                                                        |              |          |          |          |       |              |            |
|Data-Age Analysis for Multi-Rate Task Chains under Timing Uncertainty                   |Gohary 2022   | Yes      | No       | Yes      | No    | MDA          | Received   |
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
    │	├── Guenzel2023_equi.py
    │	├── Guenzel2023_equi_extension1.py
    │	├── Guenzel2023_equi_extension2.py
    │	├── Guenzel2023_inter.py
    │	├── Guenzel2023_mixed.py
    │	├── Hamann2017.py
    │	├── Kloda2018.py
    │	├── Kordon2020.py
    │	└── Martinez2020.py
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
    │	├── analyszer.py
    │	├── augmented_job_chain.py
    │	├── event_simulator.py
    │	└── scheduler.py
    ├── .gitignore
    ├── consoleInterface.py			    # Parses the given console arguments
    ├── e2eMain.py				        # Main file to start the framework
    ├── framework.py				    # Logic of the framework
    ├── graphicalInterface.py			# Starts the GUI and collects input values
    ├── helpers.py				        # Helpers for file access
    ├── LICENSE
    └── README.md
