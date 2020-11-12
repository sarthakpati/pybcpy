import os
import tarfile


TAR_MODE = "xz"


def store_file_tar(tar, file):
    fnam = os.path.basename(file)
    with tarfile.open(name=tar, mode=f"w:{TAR_MODE}") as tf:
        tf.add(file, arcname=fnam)


def restore_file_tar(tar, dest_path):
    with tarfile.open(name=tar, mode=f"r:{TAR_MODE}") as tf:
        flist = tf.getmembers()
        if len(flist) != 1:
            raise Exception("wrong number of files in archive")
        m = flist[0]
        tf.extract(m, path=dest_path)
