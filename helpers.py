'''
Basis from https://github.com/tu-dortmund-ls12-rt/end-to-end_mixed/blob/master/e2e/helpers.py
'''

import time
import pickle
import os


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
        print(f'Directory {dirname} created')


def make_output_directory():
    """creates a new directory with the current date
    and a sequential number counting up"""
    testrun = 1
    while os.path.exists(f'output/{date()}_Test{testrun:03d}/'):
        testrun+=1

    os.makedirs(f'output/{date()}_Test{testrun:03d}/')
    print(f'Directory output/{date()}_Test{testrun:03d}/ created')
    return f'output/{date()}_Test{testrun:03d}/'


def write_data(filename, data):
    file = open(filename, 'wb')
    pickle.dump(data, file)
    file.close()
    print(f'Data written to {filename}')


def load_data(filename):
    file = open(filename, 'rb')
    data = pickle.load(file)
    file.close()
    print(f'Data loaded from {filename}')
    return data
