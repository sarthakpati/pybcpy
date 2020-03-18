
import os
import stat
import time
import shutil

import argparse
import logging

from .file_utils import *
from .diff_bak_copy import DiffBackup, REPO_EXT


VERSION = "0.0.7"
VERSION_add = "this software is in alpha state. refer homepage on github for more"


class DirectoryClashException(Exception):
    pass

class SourceNoDirectoryException(Exception):
    pass


def expand_dir(path):
    return os.path.abspath(os.path.expanduser( path ))

def expand_dirs( repo, src ):
    repo = expand_dir( repo )
    src = expand_dir( src )
    return repo, src

def get_checked_dirs( repo, src ):
    repo, src = expand_dirs( repo, src )
    if repo.find( src + os.sep ) == 0:
        raise DirectoryClashException("repo can not reside inside the backup")
    if stat.S_ISDIR( get_file_info(src).st_mode ) == 0:
        raise SourceNoDirectoryException(f"{src}")
    return repo, src

def set_defaults(dbak,args):
    dbak.verbose = args.verbose
    dbak.pool = args.pool
    
def get_dbak_from_repo(args):
    repo = expand_dir( args.repo )
    dbak = DiffBackup( repo, verbose=args.verbose, debug=args.debug )
    set_defaults( dbak, args )
    return dbak

def get_dbak(args):
    repo, src = get_checked_dirs( args.repo, args.src )
    dbak = DiffBackup( repo, src, verbose=args.verbose, debug=args.debug )
    set_defaults( dbak, args )
    return dbak


def cmd_init(args):
    dbak = get_dbak( args )
    total_time, hash_time, memused, numfiles, \
                bak_dict, srcpath, repopath \
                = dbak.init_backup_repo( tarmode = args.tar )
    print( f"init done for {numfiles} files, total diskspace {memused} bytes in {total_time} sec, hashing {hash_time} sec" )

def cmd_stat(args):
    dbak = get_dbak_from_repo( args )
    bak_dict_all, read_bak_info, changed, deleted, created, \
               bak_dict_dirs_diff = dbak.get_diff()
    #print( changed, deleted, created, bak_dict_dirs_diff )
    print("changed objetcs", len( changed ))
    for f in changed:
        print( f )
    print("deleted objetcs", len( deleted ))
    for f in deleted:
        print( f )
    print("created objetcs", len( created ))
    for f in created:
        print( f )

def cmd_bak(args):
    dbak = get_dbak_from_repo( args )
    
    if args.json:
        dbak.setup(print_level=logging.NOTSET )
        
    res = dbak.write_diff_bak(comment=args.message)
    diffbaknam, numfiles, duration = res
    if args.json:
        import json
        print(json.dumps({
            "name" : diffbaknam,
            "len"  : numfiles,
            "time" : duration
            }))
    else:
        print( f"backup {diffbaknam} with {numfiles} files done in {duration} sec" )

def cmd_list(args):
    dbak = get_dbak_from_repo( args )
    baks = dbak.get_bak_list( args.full )
    for b in baks:
        print( b )

def cmd_clean(args):
    dbak = get_dbak_from_repo( args )
    del_dirs = dbak.cleanup(args.keep)
    print( "cleaned ", len(del_dirs) )
    for d in del_dirs:
        print( d )

def cmd_repair(args):
    dbak = get_dbak_from_repo( args )
    res = dbak.repair_meta()
    bak_dict, duration = res
    print( "total files in index", len(bak_dict), ", time used", duration, "sec")


def main_func():
 
    parser = argparse.ArgumentParser(prog='pybcpy', usage='python3 -m %(prog)s [options] command [cmd-options] ',
            description="""backup copy - utility for creating differential backups
            """,
            epilog="""for more information refer to https://github.com/kr-g/%(prog)s
            """
        )
    
    parser.add_argument("-v", "--version", dest='show_version', action="store_true", \
                        help="show version info and exit", default=False )

    parser.add_argument("-V", "--verbose", dest='verbose', action="store_true", \
                        help="show more info", default=False )

    parser.add_argument("-D", "--debug", dest='debug', action="store_true", \
                        help="show debug info", default=False )

    parser.add_argument("-p", "--pool", action="store", help="number of parallel processes to run where appicable", default=-1 )

    parser.add_argument("-repo", action="store", help='repo path where backup is stored, (default: %(default)s)', default="." )

    subparsers = parser.add_subparsers(help='call %(prog)s {command} --help for more', dest='cmd_name')
    
    parser_init = subparsers.add_parser('init', help='init a backup repo' )
    parser_init.add_argument('-src', type=str, help='src path to files to backup, default: %(default)s)', default=".", required=True )
    parser_init.add_argument('-tar', action="store_true", help='enable experimental tar mode (not recommened), default: %(default)s)', default=False )
    parser_init.set_defaults(func=cmd_init)

    parser_stat = subparsers.add_parser('stat', help='show the differences for the repo without creating a new backup' )
    parser_stat.set_defaults(func=cmd_stat)
    
    parser_bak = subparsers.add_parser('bak', help='create a new backup for the repo' )
    parser_bak.add_argument('-m', "-message", dest="message", type=str, help='add an additon text, default: %(default)s)', default="" )
    parser_bak.add_argument('-json', action="store_true", help='output json instead of summary text, default: %(default)s)', default=False )
    parser_bak.set_defaults(func=cmd_bak)
    
    parser_list = subparsers.add_parser('list', help='list the available backups' )
    parser_list.add_argument('-f', '--full', action="store_true", help='display more information', default=False )
    parser_list.set_defaults(func=cmd_list)
    
    parser_clean = subparsers.add_parser('clean', help='cleans the backup by removing older backups' )
    parser_clean.add_argument("-k", '-keep', type=int, help='number of backups to keep, default: %(default)s)', default=30 )
    parser_clean.set_defaults(func=cmd_clean)

    parser_repair = subparsers.add_parser('repair', help='repair the repo index and set the repo active again' )
    parser_repair.set_defaults(func=cmd_repair)

    args = parser.parse_args()
    #print( args ); return
    
    if args.show_version:
        print( "Version:", VERSION )
        print( VERSION_add )
        return

    if "func" in args:
       args.func(args)
    else:
        parser.print_help()
        #parser.print_usage()


if __name__=="__main__":

    main_func()
    

