import os

from pybcpy.file_utils import examine

from .acl import ACLinfo


class ACLrepo(object):
    def __init__(self, acl_store_dir):
        self.acl_store_dir = os.path.expanduser(acl_store_dir)

    def dumps(self, all_acl, replace_path=None, force=False):
        raise NotImplementedError

    def loads(self, replace_path=None):
        raise NotImplementedError

    def remove_sync(self, all_acl):
        raise NotImplementedError

    def read_dir(self, acl_path):
        all_files = filter(lambda x: x.find(self.acl_store_dir) != 0, examine(acl_path))
        all_acl = map(lambda x: ACLinfo(x).read().strip_path(acl_path), all_files)
        return list(all_acl)
