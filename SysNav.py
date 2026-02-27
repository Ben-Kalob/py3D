import os

def get_real_path(path : str) :
    return os.path.dirname(os.path.realpath(__file__)).replace("\\","/") + "/" + path
