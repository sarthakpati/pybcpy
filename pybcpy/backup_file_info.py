import uuid
import stat
import json

from pybcpy.file_utils import get_file_info, get_file_hash


class BackupFileInfo(object):
    def __init__(self, fnam=None, id=None):

        self.id = id if id != None else uuid.uuid4().hex
        self.fnam = fnam

    def add_basedir(self, basedir):
        self.fnam = basedir + self.fnam  # os.path.join( basedir, self.fnam )
        return self

    def remove_basedir(self, basedir):
        if self.fnam.index(basedir) == 0:
            self.fnam = self.fnam[len(basedir) :]
        return self

    def from_file(self):
        fstat = get_file_info(self.fnam)

        self.size = fstat.st_size

        self.atime = fstat.st_atime
        self.ctime = fstat.st_ctime
        self.mtime = fstat.st_mtime

        self.mode = fstat.st_mode
        self._set_mode()

        hash = get_file_hash(self.fnam) if self.is_file else None
        self.hash = hash

        return self

    def _set_mode(self):
        self.is_dir = stat.S_ISDIR(self.mode)
        self.is_file = stat.S_ISREG(self.mode)
        self.is_link = stat.S_ISLNK(self.mode)

    def from_list(v, self):  # this is not a bug
        v.fnam, v.id, v.mode, v.size, v.atime, v.mtime, v.ctime, v.hash = self
        v._patch_vals()
        return self

    def _patch_vals(v):
        v.mode = int(v.mode)
        v.size = int(v.size)
        v.atime = float(v.atime)
        v.mtime = float(v.mtime)
        v.ctime = float(v.ctime)
        v._set_mode()
        if len(v.hash) == 0:
            v.hash = None

    def _attr_iter(self):
        for n in [
            "fnam",
            "id",
            "mode",
            "size",
            "atime",
            "mtime",
            "ctime",
            "hash",
        ]:
            yield n

    def from_json(self, jstr):
        if jstr.strip().find("#") == 0:
            return None
        o = json.loads(jstr)
        for n in self._attr_iter():
            setattr(self, n, o[n])
        self._patch_vals()
        return self

    def to_dict(self):
        o = {}
        for n in self._attr_iter():
            o[n] = getattr(self, n)
        return o

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        res = (
            self.fnam == other.fnam and self.hash == other.hash and self.id == other.id
        )
        return res

    def __repr__(self):
        return (
            f"fnam={self.fnam} id={self.id} hash={self.hash}"
            + f" size={self.size}"
            + f" mtime={self.mtime} atime={self.atime} ctime={self.ctime}"
        )
