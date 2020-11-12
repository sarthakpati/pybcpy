import os

import grp
import spwd


class Group(object):
    def __init__(self):
        self.name = None
        self.member = []

    def from_grp(self, grp):
        self.name = grp.gr_name
        self.member = grp.gr_mem
        return self

    def loads(self, grp_info):
        group = grp_info.strip().split("\t")
        self.name = group[0]
        self.member = list(map(lambda x: x.strip(), group[1].split(",")))
        return self

    def dumps(self):
        return self.name + "\t" + ",".join(self.member)

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + " name: '"
            + self.name
            + "'"
            + " member: "
            + str(self.member)
            + " )"
        )


all_grps = []
glist = []
gmap = {}
gmap_keys = []


def get_all_groups():
    global all_grps
    all_grps = grp.getgrall()

    global glist
    glist = map(lambda x: Group().from_grp(x), all_grps)
    glist = sorted(glist, key=lambda x: x.name)

    global gmap
    gmap = dict(map(lambda x: (x.name, x), glist))

    global gmap_keys
    gmap_keys = sorted(gmap.keys())


def dumps(l):
    for grp in l:
        print(grp.dumps())


get_all_groups()

dumps(glist)


search_for = "sudo"

print("--- search_for found", search_for)

used = list(filter(lambda x: x.name == search_for or search_for in x.member, glist))

dumps(used)

print("--- group", search_for)

dumps([gmap[search_for]])
