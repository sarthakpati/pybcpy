import os
import stat

import glob
import time

import uuid

import csv
import shutil
from multiprocessing import Pool
import configparser
import logging

from .file_utils import (
    get_file_exists,
    get_file_info,
    get_file_size,
    ensure_dest_dir,
    examine,
)

from .backup_file_info import BackupFileInfo
from .tar_utils import store_file_tar
from .print_utils import PrintInfo


DEFAULT_DIFF_TAR_MODE = False
# DEFAULT_REPO_TAR_MODE = False
DEFAULT_CPU_POOL = -1
DEFAULT_VERBOSE = True

REPO_EXT = "_bak_repo"
REPO_PATH = "repo"
DIFF_PATH = "diff"
DIFF_FILES = "files"
META_PATH = "meta"

META_FILE = "meta.bs"
CFG_FILE = "meta.cfg"
LOG_FILE = "backup.log"

CHANGED = "changed.bs"
CREATED = "created.bs"
DELETED = "deleted.bs"

DELETED_DIR = "deleteddir.bs"

BUSY = "busy"

CFG_BASE = "backup"
CFG_REPO = "repo"
CFG_REPOID = "repoid"
CFG_SRC = "src"
CFG_PARENT = "parent"
CFG_DIFF_TAR = "tar"
CFG_COMMENT = "comment"
CFG_CREATED = "created"
CFG_ALL_FILES = "include_hidden"
CFG_ALL_FILES_Default = False
# CFG_DIFF_REPO="diff-repo"

DELIMITER = "\t"
BACKUP_NAME_DELIMITER = "_"
BACKUP_PREFIX = "bak_"


class NoRepoDirectoryException(Exception):
    pass


class SameDirectoryException(Exception):
    pass


class DiffBackup(PrintInfo):
    def __init__(
        self,
        repopath,
        srcpath=None,
        verbose=False,
        allfiles=CFG_ALL_FILES_Default,
        debug=False,
    ):

        self.setup(
            print_verbose=verbose, print_level=logging.DEBUG if debug else logging.INFO
        )

        self.repopath = repopath

        self.repofull = os.path.join(repopath, REPO_PATH)
        self.diffpath = os.path.join(repopath, DIFF_PATH)
        self.metapath = os.path.join(repopath, META_PATH)

        self.logfd = None
        self.verbose = DEFAULT_VERBOSE
        tarmode = DEFAULT_DIFF_TAR_MODE
        repoid = uuid.uuid4().hex

        if srcpath == None:
            try:
                cfg = self.read_config()
                srcpath = cfg[CFG_BASE][CFG_SRC]
                tarmode = cfg[CFG_BASE][CFG_DIFF_TAR].lower() == "true"
                repoid = cfg[CFG_BASE][CFG_REPOID]

                allfiles = cfg[CFG_BASE].get(CFG_ALL_FILES, str(CFG_ALL_FILES_Default))
                allfiles = allfiles.lower() == "true"

            except Exception as ex:
                raise NoRepoDirectoryException("not found", ex)

        self.srcpath = srcpath
        self.repoid = repoid
        self.tarmode = tarmode
        self.allfiles = allfiles

        self.pool = DEFAULT_CPU_POOL

    def set_repo_busy(self, busy=True):
        fnam = os.path.join(self.metapath, BUSY)
        if busy:
            if get_file_exists(fnam):
                raise Exception(f"repo '{self.repopath}' already marked as busy")
            with open(fnam, "w") as f:
                print(True, file=f)
        else:
            try:
                os.remove(fnam)
            except:
                self.print_w("repo not busy before")

    def get_repo_busy(self):
        return get_file_exists(os.path.join(self.metapath, BUSY))

    def __repr__(self):
        return (
            f"repopath={self.repopath}, repofull={self.repofull}, "
            f"diffpath={self.diffpath}, metapath={self.metapath}, "
            f"srcpath={self.srcpath}, tarmode={self.tarmode}, "
            f"pool={self.pool}"
        )

    def read_config(self, metapath=None):
        if metapath == None:
            metapath = self.metapath

        cfgfile = os.path.join(metapath, CFG_FILE)
        self.print_d("read config", cfgfile)
        config = configparser.ConfigParser()
        config.read(cfgfile)
        return config

    def write_config(self, metapath=None, tarmode=None, add_info=None):
        if metapath == None:
            metapath = self.metapath
        if tarmode == None:
            tarmode = self.tarmode

        config = configparser.ConfigParser()
        config[CFG_BASE] = {
            CFG_REPOID: self.repoid,
            CFG_REPO: self.repopath,
            CFG_SRC: self.srcpath,
            CFG_DIFF_TAR: tarmode,
            CFG_ALL_FILES: self.allfiles,
        }
        if add_info:
            print(add_info)
            config[CFG_BASE].update(add_info)

        cfgfile = os.path.join(metapath, CFG_FILE)
        self.print_d("write config", cfgfile)
        with open(cfgfile, "w") as f:
            config.write(f)

    def _calc_pool_size(self):
        if self.pool > 0:
            return self.pool
        threads_per_cpu = 2
        # refer to py doc of
        #  multiprocessing.cpu_count()
        #  os.cpu_count()
        # no of cpu process can use
        no_of_cpu = len(os.sched_getaffinity(0))
        return no_of_cpu * threads_per_cpu - 1

    def _get_backup_info(self, f):
        bfi = BackupFileInfo(f)
        bfi.from_file()
        return bfi

    def create_backup_info_set(self, srcpath=None):
        self.print_d("create_backup_info_set")

        start_time = time.time()

        if srcpath == None:
            srcpath = self.srcpath

        ifiles = examine(srcpath, not self.allfiles)
        bak_info = []
        with Pool(self._calc_pool_size()) as p:
            bak_info.extend(p.map(self._get_backup_info, ifiles))
        bak_info_clean = map(lambda x: x.remove_basedir(srcpath), bak_info)
        bak_dict = dict(map(lambda x: (x.fnam, x), bak_info_clean))

        stop_time = time.time()
        return bak_dict, stop_time - start_time

    @staticmethod
    def _filter_files(bakdict):
        return dict(filter(lambda x: stat.S_ISREG(x[1].mode), bakdict.items()))

    def _init_copy_single(self, f):

        relnam = f[len(self.srcpath) + 1 :]  # remove leading path and os.sep
        dest_path = os.path.join(self.repofull, relnam)

        st = get_file_info(f)
        if not stat.S_ISREG(st.st_mode):
            self.print_d(f"skipping directory {f}")
            return None

        self.print_v(f"copy {f} -> {dest_path}")
        ensure_dest_dir(dest_path)
        shutil.copy2(f, dest_path)
        # self.log( f"done {f}" )

        return f

    def init_backup_repo(self, tarmode=False):

        start_time = time.time()
        self.tarmode = tarmode

        # exception if repo is existing
        os.makedirs(self.repofull)
        os.makedirs(self.diffpath)
        os.makedirs(self.metapath)

        ifiles = examine(self.srcpath, not self.allfiles)
        numfiles = 0
        memused = 0
        with Pool(self._calc_pool_size()) as p:
            files = p.map(self._init_copy_single, ifiles)
            numfiles = numfiles + len(files)
            for f in files:
                if f is None:
                    continue
                memused += get_file_size(f)

        start_hash_time = time.time()
        bak_dict, _duration = self.create_backup_info_set()
        stop_hash_time = time.time()
        bak_dict = DiffBackup._filter_files(bak_dict)

        self.write_backup_summary(bak_dict)
        add_info = {
            CFG_CREATED: time.asctime(time.gmtime(time.time())),
        }
        self.write_config(add_info=add_info)

        stop_time = time.time()

        return (
            stop_time - start_time,
            stop_hash_time - start_hash_time,
            memused,
            numfiles,
            bak_dict,
            self.srcpath,
            self.repopath,
        )

    @staticmethod
    def _expand_dict(d):
        for _k, v in d.items():
            res = [v.fnam, v.id, v.mode, v.size, v.atime, v.mtime, v.ctime, v.hash]
            yield res

    def write_backup_summary(self, bak_dict, metafile=None, writemode="w"):
        self.print_d("write_backup_summary")
        if metafile == None:
            metafile = os.path.join(self.metapath, META_FILE)
        ensure_dest_dir(metafile)
        with open(metafile, writemode, newline="") as f:
            writer = csv.writer(f, delimiter=DELIMITER)
            writer.writerows(DiffBackup._expand_dict(bak_dict))

    def read_backup_summary(self, metafile=None):
        self.print_d("read_backup_summary")
        if metafile == None:
            metafile = os.path.join(self.metapath, META_FILE)
        backup_info = {}
        with open(metafile, "r", newline="") as f:
            reader = csv.reader(f, delimiter=DELIMITER)
            for row in reader:
                bi = BackupFileInfo()
                bi.from_list(row)
                # add to result list
                backup_info[bi.fnam] = bi
        return backup_info

    def get_unique_backup_name(self):
        return str(time.time()).replace(".", BACKUP_NAME_DELIMITER)

    def get_diff(self):
        self.print_d("get_diff")
        read_bak_info = self.read_backup_summary()
        bak_dict_all, _duration = self.create_backup_info_set()

        # remove dir entries from set
        bak_dict = DiffBackup._filter_files(bak_dict_all)

        # check if element was already in the set, get the id from old state
        for fnam, bi in bak_dict.items():
            if fnam in read_bak_info:
                bi.id = read_bak_info[fnam].id

        created = {}
        for fnam, bi in bak_dict.items():
            if fnam in read_bak_info:
                continue
            created[fnam] = bi
        self.print_v(f"created={created}")

        changed = {}
        for fnam, bi in read_bak_info.items():
            if fnam in bak_dict:
                if bi.hash == bak_dict[fnam].hash:
                    continue
                changed[fnam] = read_bak_info[fnam]
        self.print_v(f"changed={changed}")

        deleted = {}
        for fnam, bi in read_bak_info.items():
            if fnam in bak_dict:
                continue
            deleted[fnam] = bi
        self.print_v(f"deleted={deleted}")

        # dir delta list
        read_bak_dict_dirs = set(
            map(lambda x: os.path.dirname(x), read_bak_info.keys())
        )
        bak_dict_all_dirs = set(map(lambda x: os.path.dirname(x), bak_dict_all.keys()))
        bak_dict_dirs_diff = read_bak_dict_dirs - bak_dict_all_dirs

        return (
            bak_dict_all,
            read_bak_info,
            changed,
            deleted,
            created,
            bak_dict_dirs_diff,
        )

    def get_bak_list(self, full=True):
        self.print_d("get_bak_list")
        baks = glob.iglob(os.path.join(self.diffpath, "*"))
        baks = filter(lambda x: stat.S_ISDIR(get_file_info(x).st_mode), baks)
        plain = map(lambda x: os.path.basename(x), baks)
        sorted = list(plain)
        sorted.sort(reverse=True)
        if full:
            return list(
                zip(
                    sorted,
                    map(
                        lambda x: time.gmtime(
                            float(x.replace(BACKUP_NAME_DELIMITER, "."))
                        ),
                        sorted,
                    ),
                )
            )
        return sorted

    def _write_single(self, args):

        diffbaknam, diff_files, f, bi, changed, deleted, created = args

        fnam = f[1:]  # remove leading os.sep
        self.print(f"processing {f} -> {fnam}")
        repof = os.path.join(self.repofull, fnam)
        difff = os.path.join(diff_files, fnam)

        file_exists = get_file_exists(repof)
        if file_exists == True:
            self.print_v(
                f"create diff for {fnam}, {repof} exists {file_exists}, tar={self.tarmode}"
            )
            if self.tarmode == True:
                tarf = os.path.join(diff_files, bi.id + ".tar")
                self.print_v(f"write {repof} to tar {tarf}")
                ensure_dest_dir(tarf)
                store_file_tar(tarf, repof)
            else:
                self.print_v(f"copy {repof} to {difff}")
                ensure_dest_dir(difff)
                shutil.copy2(repof, difff)

        self.print_v(f"update repo for {fnam}")
        if f in changed or f in created:
            fpath = os.path.join(self.srcpath, fnam)
            self.print_v(f"copy file {fnam} -> {fpath} to repo {repof}")
            ensure_dest_dir(repof)
            shutil.copy2(fpath, repof)
        if f in deleted:
            self.print_v(f"delete file {repof} from repo")
            os.remove(repof)

        ## todo exception handling
        return f

    def _write_diff_iter(self, diffbaknam, diff_files, comb, changed, deleted, created):
        for f in comb.values():
            yield diffbaknam, diff_files, f.fnam, f, changed, deleted, created

    def write_diff_bak(self, comment=""):

        start_time = time.time()

        self.set_repo_busy(True)

        diffbaknam = self.get_unique_backup_name()
        diffbakpath = os.path.join(self.diffpath, diffbaknam)
        diff_files = os.path.join(diffbakpath, DIFF_FILES)

        self.print("---start---")

        (
            bak_dict,
            _read_bak_info,
            changed,
            deleted,
            created,
            bak_dict_dirs_diff,
        ) = self.get_diff()

        # combine to get all files
        comb = {}
        comb.update(changed)
        comb.update(deleted)
        comb.update(created)

        numfiles = 0
        with Pool(self._calc_pool_size()) as p:
            ## todo chng to starmap?
            files = p.imap(
                self._write_single,
                self._write_diff_iter(
                    diffbaknam, diff_files, comb, changed, deleted, created
                ),
            )
            for f in files:
                numfiles += 1
                self.print_v("writing backup info for", f)
                if f in changed:
                    metafile = os.path.join(diffbakpath, CHANGED)
                    self.write_backup_summary(changed, metafile, "a")
                if f in created:
                    metafile = os.path.join(diffbakpath, CREATED)
                    self.write_backup_summary(created, metafile, "a")
                if f in deleted:
                    metafile = os.path.join(diffbakpath, DELETED)
                    self.write_backup_summary(deleted, metafile, "a")

        # handling of missing dirs
        for df in bak_dict_dirs_diff:
            fpath = self.repofull + df  # [len(self.basepath):]
            self.print_v(f"missing dir {df} -> {fpath}")
            try:
                pass
                os.rmdir(fpath)  # delete dir in repo
            except Exception as ex:
                self.print_w(f"could not delete repo dir {fpath}", ex)

        if len(bak_dict_dirs_diff) > 0:
            self.print_d("writing diff dir meta file")
            metafile = os.path.join(diffbakpath, DELETED_DIR)
            with open(metafile, "w") as f:
                for dd in bak_dict_dirs_diff:
                    print(dd, file=f)
                    self.print_v(f"deletede dir {f}")

        if numfiles > 0:

            parent = 0
            try:
                parents = self.get_bak_list(False)
                parent = parents[1]
            except:
                pass  # first backup, no parent

            self.print_v("write diff backup meta")

            config = configparser.ConfigParser()
            config[CFG_BASE] = {
                CFG_REPOID: self.repoid,
                CFG_PARENT: parent,
                CFG_DIFF_TAR: self.tarmode,
                CFG_COMMENT: comment,
            }

            cfgfile = os.path.join(diffbakpath, CFG_FILE)
            with open(cfgfile, "w") as f:
                config.write(f)

            # write current repo backup set to disk
            bak_dict = DiffBackup._filter_files(bak_dict)
            self.write_backup_summary(bak_dict)

        self.print("---ende---")

        self.set_repo_busy(False)

        stop_time = time.time()

        return diffbaknam, numfiles, stop_time - start_time

    def repair_meta(self):

        start_time = time.time()

        # repopath, repo = os.path.split(self.repofull)
        bak_dict_all, _duration = self.create_backup_info_set(self.repofull)
        bak_dict = DiffBackup._filter_files(bak_dict_all)
        self.write_backup_summary(bak_dict)
        self.set_repo_busy(False)
        stop_time = time.time()

        return bak_dict, stop_time - start_time

    def cleanup(self, no_to_keep):
        if no_to_keep < 0:
            raise Exception("invalid number")
        bakups = self.get_bak_list(False)
        to_del = bakups[no_to_keep:]
        for f in to_del:
            rm_path = os.path.join(self.diffpath, f)
            self.print_v(f"remove backup {rm_path}")
            shutil.rmtree(rm_path, ignore_errors=True)
            self.print_v(f"remove {rm_path} done")
        return to_del

    def _get_diff_bs(self, baknam, bak_section):
        try:
            bs = self.read_backup_summary(
                os.path.join(self.diffpath, baknam, bak_section)
            )
        except:
            bs = None
        return bs

    def _get_del_dir(self, baknam):
        try:
            with open(os.path.join(self.diffpath, baknam, DELETED_DIR)) as f:
                bs = f.read().splitlines()
        except:
            bs = None
        return bs

    def get_diff_bsets(self, baknam):
        changed = self._get_diff_bs(baknam, CHANGED)
        created = self._get_diff_bs(baknam, CREATED)
        deleted = self._get_diff_bs(baknam, DELETED)
        deleteddir = self._get_del_dir(baknam)

        return created, changed, deleted, deleteddir
