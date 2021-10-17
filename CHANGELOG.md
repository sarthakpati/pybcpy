
# Changelog


## release v0.0.17

- refact package structure, some tools are now sub-packages to pybcpy
  - pyacltk => pybcpy.pyacltk
  - pyusrgrptk => pybcpy.pyusrgrptk
- entry point for pybcpy (refer to `setup.cfg`)
-


## release v0.0.16

- fixed continue init copy in error case, report error
- changed internal backup-set structure from csv to json 
 (each line is separate json represented object)
- added MANIFEST file for missing markdown files 
 https://github.com/kr-g/pybcpy/issues/1
-


## release v0.0.15

- fixed pypi package upload 
-


## release v0.0.14

- added `inspect` sub-cmd
  - for use with tar e.g. `pybcpy -repo your_repo inspect -include 1 | tar -cf yourarchive.tar -T -`
- 


## release v0.0.13

- added "include_all" feature in config for backup also hidden "." dot-files
- 


## release v0.0.12

- fix import in cmd line `pyusrgrptk`
- Flake8 introduced
- 

## release v0.0.11

- PEP 8
- added (first draft) new toolkit `pyusrgrptk` for backup user group information
- `pyusrgrptk` methods for searching, or listing all groups
- hierarchy view of all groups 
- list group with, or without member
- list only group member (use with filter)
-

## release v0.0.10

- restore of files
- save and restore of Linux access controll list information with module
 [`acl-toolkit`](https://github.com/kr-g/pybcpy/tree/master/pyacltk)
- 

## release v0.0.9

- added list detail cmd
-

