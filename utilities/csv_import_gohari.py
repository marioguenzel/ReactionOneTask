import csv
import os


def get_latencies_from_csv(csv_file_path):
    latencies = []
    
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)

        for row in reader:
            # values have to be adjusted, because they were previously multiplied by 1000000
            latencies.append(float(row[2])/1000000)

    # remove file, so that new values are not mixed with already paresed values
    os.remove(csv_file_path)

    return latencies