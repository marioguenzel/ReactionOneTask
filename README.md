# E2EEvaluation
Evaluation Framework for End-to-End Analyses

## Required Packages
To install the necessary (python) packages run the following commands:

```
sudo apt-get install python3-tk
pip install -v "pysimplegui==4.60.5"
pip install scipy numpy matplotlib
```
## Analyses Overview
List of papers with analyses methods relevant for the framework:

| Paper Title                                                                              | Short Name       | Periodic | Sporadic | Implicit | LET   | Result  | Status     |
|------------------------------------------------------------------------------------------|------------------|----------|----------|----------|-------|---------|------------|
| Period Optimization for Hard Real-time Distributed Automotive Systems                    | (Davare 2007)    | Yes      | (Yes)    | Yes      | No    | MRT     | Integrated |
| Synthesizing Job-Level Dependencies for Automotive Multi-rate Effect Chains              | (Becker 2016)    | Yes      | No       | Yes      | No    | MRT     | Requested  |
| End-to-end timing analysis of cause-effect chains in automotive embedded systems         | (Becker 2017)    | Yes      | ?        | ?        | Yes   | MDA,MRT | Requested  |
| Communication Centric Design in Complex Automotive Embedded Systems                      | (Hamann 2017)    | Yes      | Yes      | No       | Yes   | ?       | Integrated |
| Latency analysis for data chains of real-time periodic tasks                             | (Kloda 2018)     | Yes      | No       | Yes      | No    | ?       | Received   |
| End-to-End Timing Analysis of Sporadic Cause-Effect Chains in Distributed Systems        | (Dürr 2019)      | Yes      | Yes      | Yes      | (Yes) | ?       | Integrated |
| Evaluation of the Age Latency of a Real-Time Communicating System using the LET paradigm | (Kordon 2020)    | Yes      | No       | No       | Yes   | MDA     | Requested  |
| End-to-end latency characterization of task communication models for automotive systems  | (Martinez 2020)  | Yes      | No       | Yes      | Yes   | MDA,MRT | Requested  |
| Efficient Maximum Data Age Analysis for Cause-Effect Chains in Automotive Systems        | (Bi 2022)        | Yes      | No       | Yes      | No    | MDA     | Missing    |
| Timing Analysis of Asynchronized Distributed Cause-Effect Chains                         | (Günzel 2021)    | Yes      | (Yes)    | Yes      | Yes   | MDA,MRT | Received   |
| Timing Analysis of Cause-Effect Chains with Heterogeneous Communication Mechanisms       | (Günzel 2023)    | Yes      | Yes      | Yes      | Yes   | MRT     | Received   |
| Compositional Timing Analysis of Asynchronized Distributed Cause-effect Chains           | (Günzel 2023)    | Yes      | (Yes)    | Yes      | Yes   | MDA,MRT | Received   |
|                                                                                          |                  |          |          |          |       |         |            |
| Data-Age Analysis for Multi-Rate Task Chains under Timing Uncertainty                    | (Gohari 2022)    | Yes      | No       | Yes      | No    | MDA     | Requested  |
| Characterizing the Effect of Deadline Misses on Time-Triggered Task Chains               | (Pazzaglia 2022) | Yes      | No       | No       | Yes   | ?       | Requested  |
|                                                                                          |                  |          |          |          |       |         |            |
| End-To-End Timing Analysis in ROS2                                                       | (Teper 2022)     | ?        | ?        | ?        | ?     | ?       | Missing    |
| Latency analysis of self-suspending task chains                                          | (Kloda 2022)     | Yes      | No       | Yes      | No    | MRT     | Missing    |
| Reaction Time Analysis of Event-Triggered Processing Chains with Data Refreshing         | (Tang 2023)      | Yes      | No       | Yes      | No    | ?       | Missing    |
