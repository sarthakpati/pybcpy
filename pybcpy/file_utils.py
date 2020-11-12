import os
import stat
import glob
import time

import hashlib


DEFAULT_BLOCK_SIZE = 2 ** 16


def ensure_dest_dir(fnam):
    dir = os.path.dirname(fnam)
    os.makedirs(dir, exist_ok=True)


def get_file_exists(fnam):
    ## todo
    try:
        os.stat(fnam)
        return True
    except:
        pass
    return False


def get_file_info(fnam):
    return os.stat(fnam)


def get_file_size(fnam):
    return os.stat(fnam).st_size


def get_file_times(fnam):
    st = get_file_info(fnam)
    return st.st_atime, st.st_mtime


def touch_file_times(fnam, atime, mtime):
    os.utime(fnam, (atime, mtime))


def get_file_hash(fnam, blk_size=DEFAULT_BLOCK_SIZE):
    hm = hashlib.sha512()
    with open(fnam, "rb") as f:
        while True:
            buf = f.read(blk_size)
            if len(buf) == 0:
                break
            hm.update(buf)
    digest = hm.hexdigest()
    return digest


def examine(fpath):
    fpath = os.path.expanduser(fpath)
    file_list = glob.iglob(fpath + os.sep + "**", recursive=True)
    return file_list
