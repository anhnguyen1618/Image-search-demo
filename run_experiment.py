from subprocess import Popen

models = ["resnet", "mobilenet", "custom", "inception", "vgg16", "vgg19"]

result_size = 7
relevant = 10

def gen_command(model):
    return f"python3 score.py -u http://serving-{model}-mongo.rahtiapp.fi/search?json=true -s {result_size} -r {relevant}"

def execute(cmd):
    return Popen(cmd.split(" "))

procs = [execute(gen_command(model)) for model in models]
for p in procs:
    p.wait()
    