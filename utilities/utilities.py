import uuid

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
