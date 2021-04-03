import os
import glob
import pathlib

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


def examine(fpath, exclude_hidden=True):
    fpath = os.path.expanduser(fpath)

    def iter_recur_files(fpath):
        files = os.listdir(fpath)
        for f in files:
            if exclude_hidden and f[0] == ".":
                # same behaviour as glob "/**"
                continue
            fnam = os.path.join(fpath, f)
            yield fnam
            p = pathlib.Path(fnam)
            if p.is_dir():
                yield from iter_recur_files(fnam)

    return iter_recur_files(fpath)
