
import os
import glob

from pybcpy.file_utils import examine
from pybcpy.__main__ import VERSION

from .acl import ACLinfo

from .flat import ACLfile
from .tree import ACLtree


## todo remove
# just sample path
acl_path = "/home/benutzer/Bilder"
acl_store = "/home/benutzer/Downloads/acl_list.txt"
acl_store_dir = "/home/benutzer/Downloads/acl"
## end-of todo remove


def main_func_tree():
    
    flat = ACLfile(acl_store)
    repo = ACLtree(acl_store_dir)
    
    # dont expand to original full path
    all_acl = flat.loads(replace_path="")
        
    #print( all_acl )

    repo.dumps(all_acl)

    #print( list(loads(acl_store_dir) ))

    print(repo.remove_sync(all_acl))
    

def main_func():
    
    # read all acl in a directory
    all_acl = (map( lambda x : ACLinfo(x).read().strip_path(acl_path), examine(acl_path) ))

    repo = ACLfile(acl_store)

    repo.dumps( all_acl, acl_path )   

    all_acl = repo.loads()

    for acl in all_acl:
        print( acl.dumps() )
        
    print( all_acl )

