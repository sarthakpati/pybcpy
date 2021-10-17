
## BACKLOG

- quite mode
- rework logging info, level, and behaviour
- catch exception for intermediate deleted files during bak process
- stats also for other tasks
- partial backup -> inner sub folder
- proper testing pending. if execution breaks please create an issue on github.
- ~~no restore supported as of now.~~
- ~~no support of permission objects e.g. ACLs, or Groups.~~
-

## KNOWN BUGS

- delete dir in repo fails when not empty
- 

## LIMITATIONS

- proper error messages, read exception error text properly
- no grafical (GUI) tool available, only cmd-line.
- no restore from a tar-mode backup repo
- tar mode is added as experimental feature (might be dropped in future)
- no full support of empty directories.
- no logging to syslog.
- no file chunk difference calculation for big files.
- no SSH, FTP, HTTP support. use of mounted device only.
- no support for excluding sub-directories.
- no root directory backup support.
-
