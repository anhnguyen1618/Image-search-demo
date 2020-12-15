import argparse, requests, os, time
import mlflow 
from stats import get_histogram

dataset_dir = "./sample"
histogram = get_histogram(dataset_dir)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = ["jpg", "png", "jpeg"]
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_dir(dir_path):
    return [
        file for file in os.listdir(dir_path)
        if allowed_file(file)
    ]

def evaluate(results, file_name, num_results, num_relevant):
    true_positive = 0
    file_name = file_name.split("_image")[0]
    for item in results:
        original_file_name = item["url"].split("/")[-1].split("_image")[0]
        if original_file_name == file_name:
            true_positive += 1

    precision = true_positive * 1.0 / num_results
    recall = true_positive * 1.0 / histogram.get(file_name, num_results) 
    return precision, recall


def benchmark(dir_path, url, model_name, result_size = 7, num_relevant=10, algo = "bruteforce", num_index = 1, num_serving = 1):
    with mlflow.start_run():
        sum_precision = 0
        sum_recall = 0

        file_names = read_dir(dir_path)
        num_files = 0 
        duration = 0
        experiment_start_time = time.time()
        for file_name in file_names:
            files = {'record': open(f"{dir_path}/{file_name}",'rb')}
            
            start = time.time()
            res = requests.post(url, files=files)
            duration += time.time() - start
            if res.status_code != 200:
                print("Error ", url, file_name, res.reason)
                continue
            # print(res.status_code, file_name, res.reason)
            precision, recall = evaluate(res.json(), file_name, result_size, num_relevant)
            sum_precision += precision
            sum_recall += recall
            num_files += 1
            # print(url, len(res.json()), result_size)
            # break
            # print(f"{file_name}: {precision}, {recall}")
            # break 

        mlflow.log_artifact("./configs/config.json")
        mlflow.log_param("model", model_name)
        mlflow.log_param("result_size", result_size)
        # mlflow.log_param("num_total_relevant", num_relevant)
        mlflow.log_param("algorithm", algo)
        mlflow.log_param("num_index", num_index)
        mlflow.log_param("num_serving", num_serving)

        precision = sum_precision / num_files 
        recall = sum_recall / num_files
        avg_duration = duration / num_files

        experiment_duration = time.time() - experiment_start_time

        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("avg_duration_per_request", avg_duration)
        mlflow.log_metric("total_test", num_files)
        mlflow.log_metric("experiment_duration", experiment_duration)

        print(f"url: {url}") 
        print(f"Precision: {precision}, Recall: {recall}, Avg duration: {avg_duration} s/req")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str, help="dataset dir to calculate precision/recall")
    parser.add_argument("-u", "--url", type=str, help="url to test")
    parser.add_argument("-s", "--size", type=int, help="result size")
    parser.add_argument("-r", "--relevant", type=int, help="num relevant in db")
    parser.add_argument("-a", "--algo", type=str, help="clustering algorithm")
    parser.add_argument("-i", "--index", type=int, help="num index")
    parser.add_argument("-se", "--serving", type=int, help="num serving")
    args = parser.parse_args()

    dir_path = args.dir or "./dataset"
    pre_url = args.url or "http://serving-mobilenet-mongo.rahtiapp.fi/search?json=true"
    size = args.size or 7
    num_relevant = args.relevant or 10
    algo = args.algo or "bruteforce"
    num_index = args.index or 1
    num_serving= args.serving or 1

    url = f"{pre_url}&size={size}"
    model = url.split("serving")[-1].split("-")[1]
    benchmark(dir_path, url, model, size, num_relevant, algo, num_index, num_serving)

