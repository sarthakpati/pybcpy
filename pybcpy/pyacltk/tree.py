import os
import glob

from .acl import ACLinfo
from .repo import ACLrepo


class ACLtree(ACLrepo):
    def dumps(self, all_acl, replace_path=None, force=False):
        for acl in all_acl:
            path = self.acl_store_dir + acl.fnam
            os.makedirs(path, exist_ok=True)
            old_acl_dump = None
            fnam = os.path.join(path, "acl.txt")
            if force == False:
                try:
                    with open(fnam, "r") as f:
                        old_acl_dump = ACLinfo().loads(f.read()).dumps()
                except:
                    pass
                    # print("file not found", fnam)
            acl_dump = acl.dumps()
            if old_acl_dump != None and old_acl_dump == acl_dump:
                # print("skip", acl)
                continue
            with open(fnam, "w") as f:
                # print("write", acl)
                f.write(acl_dump)

    def loads(self, replace_path=None):
        fnam = self.acl_store_dir + os.sep + "**" + os.sep + "acl.txt"
        files = list(glob.iglob(fnam, recursive=True))
        all_acl = []
        for file in files:
            with open(file) as f:
                cont = f.read()
                acl = ACLinfo().loads(cont)
                acl.add_path(replace_path)
                all_acl.append(acl)
        return all_acl

    def remove_sync(self, all_acl):
        all_acl_dict = dict(list(map(lambda x: (x.fnam, x), all_acl)))
        cur_acl = self.loads()
        to_remove = filter(lambda x: x.fnam not in all_acl_dict, cur_acl)
        to_remove = sorted(to_remove, key=lambda x: len(x.fnam), reverse=True)
        for acl in to_remove:
            pnam = self.acl_store_dir + acl.fnam
            fnam = pnam + os.sep + "acl.txt"
            print("rm", fnam)
            os.remove(fnam)
            print("rm", pnam)
            os.rmdir(pnam)
        return to_remove
