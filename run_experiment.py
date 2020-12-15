from subprocess import Popen
import argparse

models = ["resnet", "mobilenet", "custom", "inception", "vgg16", "vgg19"]

result_size = 7
relevant = 10

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--algo", type=str, help="clustering algorithm")
parser.add_argument("-i", "--index", type=int, help="num index")
parser.add_argument("-se", "--serving", type=int, help="num serving")

args = parser.parse_args()

algorithm = args.algo or "brute"
num_index = args.index or 1
num_serving = args.serving or 1

def gen_command(model):
    return f"python3 score.py -u http://serving-{model}-mongo.rahtiapp.fi/search?json=true -s {result_size} -r {relevant} -a {algorithm} -i {num_index} -se {num_serving}"

def execute(cmd):
    return Popen(cmd.split(" "))

procs = [execute(gen_command(model)) for model in models]
for p in procs:
    p.wait()
    