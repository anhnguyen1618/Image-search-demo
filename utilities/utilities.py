import uuid, os
import sys
import logging
import logging.config
# ================== Logger ================================
def get_pod_name():
    host_file = open("/etc/hostname")
    pod_name = host_file.read().split("\n")[0]
    return pod_name

def Logger(file_name = get_pod_name()):
    log_dir = "tmp/logs" 
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    formatter = logging.Formatter(fmt='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                                    datefmt='%Y/%m/%d %H:%M:%S') # %I:%M:%S %p AM|PM format
    logging.basicConfig(filename = f"{log_dir}/{file_name}.log", format= '%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                                    datefmt='%Y/%m/%d %H:%M:%S', filemode = 'w', level = logging.INFO)
    log_obj = logging.getLogger()
    log_obj.setLevel(logging.DEBUG)
    # log_obj = logging.getLogger().addHandler(logging.StreamHandler())

    # console printer
    # screen_handler = logging.StreamHandler(stream=sys.stdout) #stream=sys.stdout is similar to normal print
    # screen_handler.setFormatter(formatter)
    # logging.getLogger().addHandler(screen_handler)

    log_obj.info("Logger object created successfully..")
    return log_obj
'''
Take convert file name in the format name.extension to name.uuid.extenstion 
'''
def uniq_file_name(name):
    name = name.split("/")[-1]
    parts = name.split(".")
    if len(parts) >= 2:
        file_extenstion = parts[-1]
        parts.append(file_extenstion)

        uniq_part = str(uuid.uuid1())
        parts[-2] = uniq_part
    return ".".join(parts)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = ["jpg", "png", "jpeg"]
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



