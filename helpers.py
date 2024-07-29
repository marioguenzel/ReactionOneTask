"""
Basis from https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed/blob/master/e2e/helpers.py
"""

import time
import pickle
import os
import csv


def time_now():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time


def date():
    t = time.localtime()
    current_date = time.strftime("%Y-%m-%d", t)
    return current_date


def check_or_make_directory(dirname):
    """check if the folder exists, otherwise create it"""
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def make_output_directory():
    """creates a new directory with the current date
    and a sequential number counting up"""
    testrun = 1
    while os.path.exists(f'output/{date()}_Test{testrun:03d}/'):
        testrun+=1

    os.makedirs(f'output/{date()}_Test{testrun:03d}/')
    return f'output/{date()}_Test{testrun:03d}/'


def write_data(filename, data):
    file = open(filename, 'wb')
    pickle.dump(data, file)
    file.close()


def load_data(filename):
    file = open(filename, 'rb')
    data = pickle.load(file)
    file.close()
    return data


def export_to_csv(filename, names, latencies):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(names)
        for i in range(len(latencies[0])):
            writer.writerow([latencies[j][i] for j in range(len(latencies))])
