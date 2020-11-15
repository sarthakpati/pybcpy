import os
import shutil

from .file_utils import ensure_dest_dir


## todo
## different storage backends


class Storage(object):
    def __init__(self, srcpath, destpath):
        self.srcpath = srcpath
        self.destpath = destpath

        raise (NotImplementedError("not yet used"))

    def _paths(self, fnam):
        src = os.sep.join(self.srcpath, fnam)
        dest = os.sep.join(self.destpath, fnam)
        return src, dest

    def store(self, fnam):
        src, dest = self._paths(fnam)
        ensure_dest_dir(dest)
        self._store(src, dest)

    # overload this
    def _store(self, src, dest):
        shutil.copyfile(src, dest)

    def restore(self, fnam):
        src, dest = self._paths(fnam)
        ensure_dest_dir(src)
        self._restore(dest, src)

    # overload this
    def _restore(self, dest, src):
        shutil.copyfile(dest, src)
