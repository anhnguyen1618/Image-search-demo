import os

def get_histogram(dataset_dir):
    histogram = {}

    for file_name in os.listdir("./sample"):
        file_name = file_name.split("_image")[0]
        if file_name in histogram:
            histogram[file_name] += 1
        else:
            histogram[file_name] = 1
    return histogram