import argparse

from pybcpy.__main__ import VERSION, VERSION_add

from .usrgrptk import GroupRepo, dumps


_verbose = False


def print_v(*args):
    if _verbose:
        print("#", *args)


def main_func():

    parser = argparse.ArgumentParser(
        prog="pyusrgrptk",
        usage="python3 -m %(prog)s [options]",
        description="""
                user group toolkit - tool for tracking user group changes
                output format is in detail mode:
                <group-name> <tab> <comma-separated-user-list>.
                in normal mode only group name is shown.
                IMPORTANT: %(prog)s cmd-line interface is quite simple,
                but not all flag combinations make sense or produce the
                expected output. do proper test specific use-cases.
            """,
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
        "-f",
        "--repo",
        type=str,
        dest="repo_file",
        action="store",
        help="path where user group summary file is located (default: %(default)s)",
        default="~/.grpinfo",
    )

    parser.add_argument(
        "-read",
        "--read-summary",
        dest="read_os",
        action="store_false",
        help="read group data from summary file instead from os",
        default=True,
    )

    parser.add_argument(
        "-u",
        "--update",
        dest="update",
        action="store_true",
        help="update summary file with current system group info",
        default=False,
    )

    parser.add_argument(
        "--find",
        "--filter",
        dest="filter",
        action="store",
        help="search filter on group",
        default=None,
    )

    parser.add_argument(
        "-em",
        "--empty-member",
        dest="empty_member",
        action="store_true",
        help="list only groups with no member",
        default=False,
    )

    parser.add_argument(
        "-m",
        "--with-member",
        dest="with_member",
        action="store_true",
        help="list only groups with member",
        default=False,
    )

    parser.add_argument(
        "-wu",
        "--where-used",
        dest="where_used",
        action="store_true",
        help="search in group and member sections",
        default=False,
    )

    parser.add_argument(
        "-nd",
        "--no-detail",
        dest="show_detail",
        action="store_false",
        help="show full group detail",
        default=True,
    )

    parser.add_argument(
        "-nn",
        "--no-name",
        dest="hide_name",
        action="store_true",
        help="hide group name in ouput",
        default=False,
    )

    parser.add_argument(
        "-ml",
        "--multi-line",
        dest="show_multiline",
        action="store_true",
        help="display member in separate rows",
        default=False,
    )

    parser.add_argument(
        "-a",
        "--all",
        dest="show_all",
        action="store_true",
        help="show group detail",
        default=False,
    )

    parser.add_argument(
        "--hier",
        "--hierarchy",
        dest="show_hierarchy",
        action="store_true",
        help="show hierarchy of groups, independed groups first",
        default=False,
    )

    args = parser.parse_args()
    if args.verbose:
        global _verbose
        _verbose = args.verbose
        print_v("args", args)

    if args.show_version:
        print("Version:", VERSION)
        print(VERSION_add)
        return

    repo = GroupRepo(args.repo_file)

    if args.read_os == True:
        print_v("os read current")
        repo.read_current()
    else:
        print_v("repo read current")
        repo.from_store()

    if args.update == True and args.read_os == True:
        print_v("write repo")
        repo.write_store()

    if args.filter != None:
        print_v(
            "filter=",
            args.filter,
            ", where-used=",
            args.where_used,
            ", detail=",
            args.show_detail,
            "hide-name",
            args.hide_name,
            "show_multiline",
            args.show_multiline,
        )
        used = []
        if args.where_used:
            used = repo.where_used(args.filter)
        else:
            used = [repo.find(args.filter)]
        dumps(
            used,
            full=args.show_detail,
            hide_name=args.hide_name,
            show_multiline=args.show_multiline,
        )

    if args.empty_member:
        print_v("list groups with no member")
        dumps(repo.list_no_member(), full=args.show_detail)

    if args.with_member:
        print_v("list groups with member")
        dumps(
            repo.list_with_member(),
            full=args.show_detail,
            hide_name=args.hide_name,
            show_multiline=args.show_multiline,
        )

    if args.show_all:
        print_v("list all")
        dumps(repo.list_all(), full=args.show_detail, hide_name=args.hide_name)

    if args.show_hierarchy:
        print_v("list all hierarchy")
        dumps(repo.list_hierachy(), full=True)


if __name__ == "__main__":

    main_func()
