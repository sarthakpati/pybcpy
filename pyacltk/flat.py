import os

from pybcpy.file_utils import ensure_dest_dir
from .acl import ACLinfo
from .repo import ACLrepo


class ACLfile(ACLrepo):
    def dumps(self, all_acl, replace_path=None, force=False):
        all_acl = sorted(all_acl, key=lambda x: x.fnam.lower())
        fnam = self.acl_store_dir
        with open(fnam, "w") as f:
            if replace_path:
                f.write("#")
                f.write(replace_path)
                f.write("\n")
            for acl in all_acl:
                f.write(acl.dumps())
                f.write("\n")

    def loads(self, replace_path=None):
        fnam = os.path.expanduser(self.acl_store_dir)
        ensure_dest_dir(fnam)
        with open(fnam, "r") as f:
            inp = f.read()
        lines = list(filter(lambda x: len(x.strip()) > 0, inp.splitlines()))
        path = None
        if lines[0][0] == "#":
            path = lines.pop(0)[1:]
        if replace_path != None:
            path = replace_path
        all_acl = []
        for line in lines:
            if line[0] == "#":
                continue
            acl = ACLinfo().loads(line)
            acl.add_path(path)
            all_acl.append(acl)
        return all_acl

    def remove_sync(self, all_acl):
        pass
