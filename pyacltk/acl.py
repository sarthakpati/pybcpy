import os
import stat
import grp


class ACLinfo(object):
    def __init__(self, fnam=None):
        self.fnam = fnam

    def read(self):
        self.stat = os.stat(self.fnam)
        self.mode = self.stat.st_mode
        self.mode_file = stat.filemode(self.mode)
        self.uid = self.stat.st_uid
        self.uid_name = grp.getgrgid(self.stat.st_uid).gr_name
        self.gid = self.stat.st_gid
        self.gid_name = grp.getgrgid(self.stat.st_gid).gr_name
        return self

    def write(self):
        os.chmod(self.fnam, self.mode)
        os.chown(self.fnam, self.uid, self.gid)

    def strip_path(self, path):
        if self.fnam.find(path) == 0:
            self.fnam = self.fnam[len(path) :]
            return self
        raise Exception("path not found")

    def add_path(self, path):
        if path != None:
            self.fnam = path + self.fnam
        return self

    def dumps(self):
        return "\t".join(
            [self.fnam, str(self.mode), self.mode_file, self.uid_name, self.gid_name]
        )

    def loads(self, acl_info):
        acl = acl_info.strip().split("\t")
        self.fnam = acl[0]
        self.mode = int(acl[1])
        self.mode_file = stat.filemode(self.mode)
        self.uid_name = acl[3]
        self.uid = grp.getgrnam(self.uid_name).gr_gid
        self.gid_name = acl[4]
        self.gid = grp.getgrnam(self.gid_name).gr_gid
        return self

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + " fnam: "
            + self.fnam
            + " mode: "
            + str(self.mode)
            + "/"
            + self.mode_file
            + " uid: "
            + str(self.uid)
            + "/"
            + self.uid_name
            + " gid: "
            + str(self.gid)
            + "/"
            + self.gid_name
            + " )"
        )
