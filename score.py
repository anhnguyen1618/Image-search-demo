import argparse, requests, os, time

def allowed_file(filename):
    ALLOWED_EXTENSIONS = ["jpg", "png", "jpeg"]
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_dir(dir_path):
    return [
        file for file in os.listdir(dir_path)
        if allowed_file(file)
    ]

def evaluate(results, file_name):
    print(results)
    true_positive = 0
    num_relevant = 10 
    num_results = 7 
    file_name = file_name.split("_")[0]
    for item in results:
        original_file_name = item["url"].split("/")[-1].split("_")[0]
        if original_file_name == file_name:
            true_positive += 1

    precision = true_positive * 1.0 / num_results
    recall = true_positive * 1.0 / num_relevant
    return precision, recall




def benchmark(dir_path, url):
    sum_precision = 0
    sum_recall = 0

    file_names = read_dir(dir_path)
    num_files = len(file_names)
    duration = 0
    for file_name in file_names:
        files = {'record': open(f"{dir_path}/{file_name}",'rb')}
        
        start = time.time()
        res = requests.post(url, files=files)
        duration += time.time() - start
        print(res.status_code, file_name, res.reason)
        precision, recall = evaluate(res.json(), file_name)
        sum_precision += precision
        sum_recall += recall
        print(f"{file_name}: {precision}, {recall}")

    print(f"url: {url}") 
    print(f"Precision: {sum_precision / num_files}, Recall: {sum_recall / num_files}, Avg duration: {duration / num_files} s/req")
    print("---------------------------")


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", type=str, help="dataset dir to calculate precision/recall")
parser.add_argument("-u", "--url", type=str, help="url to test")
args = parser.parse_args()

if __name__ == "__main__":
    dir_path = args.dir or "./dataset"
    url = args.url or "http://serving-custom-mongo.rahtiapp.fi/search?json=true&&size=7"
    benchmark(dir_path, url)

