
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# pybackup - pybcpy

`pybcpy - python backup copy` is a set of simple (but powerfull) file based backup tools.

## `pybcpy`
for creating differential backups.

file differences are identified by using SHA512 algorithm, instead of comparing date and size.

pybcpy is designed to run in a multiprocessor environment. where possible the tasks
are executed on available cpu cores in parallel.

pybcpy is not a system recovery replacement - it deals with user data files.

## `pyacltk`
to backup Linux ACL information

## `pyusrgrptk`
to backup user group information


###
cmd line usage of all tools described below.


# Platform

Mostly Platform indepentend. Tested on Python3, and Linux.

[`acl-toolkit`](https://github.com/kr-g/pybcpy/tree/master/pyacltk)
only works on Linux, or Unix, or Posix

[`usergroup-toolkit`](https://github.com/kr-g/pybcpy/tree/master/pyusrgrptk)
only works on Linux, or Unix, or Posix


# Development status

Alpha state, use on your own risk!!!

read [`CHANGELOG`](https://github.com/kr-g/pybcpy/blob/master/CHANGELOG.md)
for latest, or upcoming news.

Experimental prototype for evaluating the further efforts of a backup tool


# Limitations

read [`BACKLOG`](https://github.com/kr-g/pybcpy/blob/master/BACKLOG.md)
for latest, or upcoming news.


# Support and Donnation

if you like the tool and want to support the next version,
or buy me a coffee - please make a donation with 
[github sponsors](https://github.com/sponsors/kr-g/)


# License

all included tools shipped with `pybcpy` are dual-licensed. read properly.

- private license: `pybcpy` is free for "non-commercial" individuals,
 except when its installed as part of an business service (read commercial license below).
- commercial license: all business related usage is not free of charge.
 also selling derived parts, or ports (to other Platform) of this software falls under this section.
 installing this software on private systems as part of a business service falls under this section.
 using in-house, or as part of a ASP service falls under this section.
 individual users like freelancers, or doing other kind of business falls under this section.
 NGOs, Universities, and other organizations falls under this section.
 for evaluation purposes a free 30 days period is granted.
 
please send me an email (k.r.goger+pybcpy.license@gmail.com) to get a quote,
or clarify license related questions. 
 
for general license information refer to the pybcpy github repo under
(https://github.com/kr-g/pybcpy/), or (https://github.com/kr-g/pybcpy/blob/master/LICENSE)


# cmd line summary

## cmd line usage pybcpy

    usage: python3 -m pybcpy [options]

    backup copy - utility for creating differential backups

    positional arguments:
      {init,stat,bak,list,restore,clean,repair,inspect}
                            call pybcpy {command} --help for more
        init                init a backup repo
        stat                show the differences for the repo without creating a new backup
        bak                 create a new backup for the repo
        list                list the available backups
        restore             restore file from repo/ backup
        clean               cleans the backup by removing older backups
        repair              repair the repo index and set the repo active again
        inspect             inspect the bakup repo and differences. list all files within the inspect range.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show version info and exit
      -V, --verbose         show more info
      -D, --debug           show debug info
      -p POOL, --pool POOL  number of parallel processes to run where aplicable
      -repo REPO            repo path where backup is stored, (default: .)

    for more information refer to https://github.com/kr-g/pybcpy


### hints
    
each command offers specific help info. display with `-h` option
   
    python3 -m pybcpy -repo 'target-repo' bak -h 


## cmd line usage acl toolkit 

    usage: python3 -m pybcpy.pyacltk [options]

    acl toolkit - tool for manage ACL (access control list)

    optional arguments:
      -h, --help       show this help message and exit
      -v, --version    show version info and exit
      -V, --verbose    show more info
      -src ACL_PATH    src path to files to backup ACL, default: .)
      -repo ACL_STORE  repo path where ACL summary is stored, (default: .acl)
      -flat            use a file as storage, default is folder storage
      -init, -i        creates a new ACL summary
      -update, -u      updates an existing ACL summary
      -setacl, -s      set file ACL from ACL summary, make sure to have sufficient rights

    for more information refer to pybcpy project on https://github.com/kr-g/pybcpy


## cmd line usage user-group toolkit 

    usage: python3 -m pybcpy.pyusrgrptk [options]

    user group toolkit - tool for tracking user group changes output format is in
    detail mode: <group-name> <tab> <comma-separated-user-list>. in normal mode
    only group name is shown. IMPORTANT: pyusrgrptk cmd-line interface is quite
    simple, but not all flag combinations make sense or produce the expected
    output. do proper test specific use-cases.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show version info and exit
      -V, --verbose         show more info
      -f REPO_FILE, --repo REPO_FILE
                            path where user group summary file is located
                            (default: ~/.grpinfo)
      -read, --read-summary
                            read group data from summary file instead from os
      -u, --update          update summary file with current system group info
      --find FILTER, --filter FILTER
                            search filter on group
      -em, --empty-member   list only groups with no member
      -m, --with-member     list only groups with member
      -wu, --where-used     search in group and member sections
      -nd, --no-detail      show full group detail
      -nn, --no-name        hide group name in ouput
      -ml, --multi-line     display member in separate rows
      -a, --all             show group detail
      --hier, --hierarchy   show hierarchy of groups, independed groups first

    for more information refer to pybcpy project on https://github.com/kr-g/pybcpy


## basic commands for setting up, and doing backups, and housekeeping

some commonly used samples

    python3 -m pybcpy -repo 'target-repo' init -src 'your-directory'
    
    python3 -m pybcpy -repo 'target-repo' bak -m "your optional comment"
    
    python3 -m pybcpy -repo 'target-repo' list
    
    # list the changes in the last backup
    python3 -m pybcpy -repo 'target-repo' list 0 
    
    # restore from repo
    python3 -m pybcpy -repo 'target-repo' restore 'your-file' -version -
    
    # restore from repo with version number as returned by list cmd
    python3 -m pybcpy -repo 'target-repo' restore 'your-file' -version 4
    
    # keep at max 30 diff backups
    python3 -m pybcpy -repo 'target-repo' clean -keep 30


# installation
    
all `pybcpy` tools are available on pypi and can be installed from there with

    python3 -m pip install pybcpy
    

