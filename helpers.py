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


def check_or_make_output_directory(dirname):
    """check if the folder exists, otherwise create it,
    returns the path of the created directory"""
    testrun = 1
    while os.path.exists(f'{dirname}{date()}_Test{testrun:03d}/'):
        testrun+=1

    os.makedirs(f'{dirname}{date()}_Test{testrun:03d}/')
    print(f'Directory {dirname}{date()}_Test{testrun:03d}/ created')
    return f'{dirname}{date()}_Test{testrun:03d}/'


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
