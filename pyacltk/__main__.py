import os

import argparse

from pybcpy.__main__ import VERSION, VERSION_add
from pybcpy.file_utils import get_file_exists

from .flat import ACLfile
from .tree import ACLtree


def main_func():

    parser = argparse.ArgumentParser(
        prog="pyacltk",
        usage="python3 -m %(prog)s [options]",
        description="""acl toolkit - tool for manage ACL (access control list) """,
        epilog="""for more information refer to pybcpy project on
                        https://github.com/kr-g/pybcpy
            """,
    )

    parser.add_argument(
        "-v",
        "--version",
        dest="show_version",
        action="store_true",
        help="show version info and exit",
        default=False,
    )

    parser.add_argument(
        "-V",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="show more info",
        default=False,
    )

    parser.add_argument(
        "-src",
        type=str,
        dest="acl_path",
        help="src path to files to backup ACL, default: %(default)s)",
        default=".",
    )
    parser.add_argument(
        "-repo",
        action="store",
        dest="acl_store",
        help="repo path where ACL summary is stored, (default: %(default)s)",
        default=".acl",
    )

    parser.add_argument(
        "-flat",
        dest="flat",
        action="store_true",
        help="use a file as storage, default is folder storage",
        default=False,
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-init",
        "-i",
        dest="init",
        action="store_true",
        help="creates a new ACL summary",
        default=False,
    )
    group.add_argument(
        "-update",
        "-u",
        dest="update",
        action="store_true",
        help="updates an existing ACL summary",
        default=False,
    )
    group.add_argument(
        "-setacl",
        "-s",
        dest="write",
        action="store_true",
        help="set file ACL from ACL summary, make sure to have sufficient rights",
        default=False,
    )

    args = parser.parse_args()
    if args.verbose:
        print("args", args)

    if args.show_version:
        print("Version:", VERSION)
        print(VERSION_add)
        return

    acl_store = os.path.expanduser(args.acl_store)
    acl_path = os.path.expanduser(args.acl_path)

    repo = ACLtree(acl_store) if args.flat == False else ACLfile(acl_store)

    if args.init:

        if get_file_exists(acl_store):
            raise Exception("repo dir already exists")

        all_acl = repo.read_dir(acl_path)
        if args.verbose:
            print("found", all_acl)
        repo.dumps(all_acl, replace_path=acl_path)
        return

    if args.update:
        all_acl = repo.read_dir(acl_path)
        repo.dumps(all_acl, replace_path=acl_path)
        removed = repo.remove_sync(all_acl)
        if args.verbose:
            print("removed", removed)
        return

    if args.write:
        all_acl = repo.loads(replace_path=acl_path)
        if args.verbose:
            print("ACL", all_acl)
        for acl in all_acl:
            acl.write()
            if args.verbose:
                print("set", acl)
        return

    parser.print_help()


if __name__ == "__main__":

    main_func()
