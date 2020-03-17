
# pybackup - pybcpy

`pybcpy - python backup copy` is a simple file based backup copy tool for creating differential backups.

file differences are identified by using SHA512 algorithm, instead of comparing date and size.

pybcpy is designed to run in a multiprocessor environment. where possible the tasks are executed on available cpu cores in parallel.

pybcpy is not a system recovery replacement - it deals with user data files.


## Platform

Platform indepentend. Tested on Python3, and Linux

## Development status

Alpha state, use on your own risk!!!

Experimental prototype for evaluating the further efforts of a simple backup tool


## Limitations

- proper testing pending. if execution breaks please create an issue on github.
- proper error messages, read exception error text properly
- no grafical (GUI) tool available, only cmd-line.
- no restore supported as of now.
- no full support of empty directories.
- no logging to syslog.
- no support of permission objects e.g. ACLs, or Groups.
- no file chunk difference calculation for big files.
- no SSH, FTP, HTTP support. use of mounted device only.
- no support for excluding sub-directories.
- no root directory backup support.
- tar mode is added as experimental feature (might be dropped in future)


## Support and Donnation

if you like the tool and want to support the next step, or buy me a coffee - please make a donation:

EURO | USD |
-----|-----|
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=VVRPWLR3ZH27G&source=url) | [![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XRN4LJ4673RTL&source=url) |


# License

`pybcpy` is dual-licensed. read properly.

- private license: `pybcpy` is free for "non-commercial" individuals, except when its installed as part of an business service (read commercial license below).
- commercial license: all business related usage is not free of charge.
 also selling derived parts, or ports (to other Platform) of this software falls under this section.
 installing this software on private systems as part of a business service falls under this section.
 using in-house, or as part of a ASP service falls under this section.
 individual users like freelancers, or doing other kind of business falls under this section.
 NOGs, and other organizations falls under this section.
 for evaluation purposes a free 30 days period is granted.
 
please send me an email (k.r.goger+pybcpy.license@gmail.com) to get an offer,
or clarify license related questions.
 
for general license information refer to the pybcpy github repo under (https://github.com/kr-g/pybcpy/), or (https://github.com/kr-g/pybcpy/blob/master/LICENSE)


## cmd line usage

    usage: python3 -m pybcpy [options] command [cmd-options] 

    backup copy - utility for creating differential backups

    positional arguments:
      {init,stat,bak,list,clean,repair}
                            call pybcpy {command} --help for more
        init                init a backup repo
        stat                show the differences for the repo without creating a
                            new backup
        bak                 create a new backup for the repo
        list                list the available backups
        clean               cleans the backup by removing older backups
        repair              repair the repo index and set the repo active again

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show version info and exit
      -V, --verbose         show more info
      -D, --debug           show debug info
      -p POOL, --pool POOL  number of parallel processes to run where appicable
      -repo REPO            repo path where backup is stored, (default: .)

    for more information refer to https://github.com/kr-g/pybcpy


## basic commands for setting up, and doing backups, and housekeeping

some commonly used samples

    python3 -m pybcpy -repo 'target-repo' init -src 'your-directory'
    
    python3 -m pybcpy -repo 'target-repo' bak -m "your optional comment"
    
    python3 -m pybcpy -repo 'target-repo' list
    
    python3 -m pybcpy -repo 'target-repo' clean -keep 30
    
## hints
    
each command offers specific help info. display with `-h` option
   
    python3 -m pybcpy -repo 'target-repo' bak -h 

## installation
    
pybcpy is available on pypi and can be installed from there with

    python3 -m pip install pybcpy
    

