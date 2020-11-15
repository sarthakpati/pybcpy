import os

import grp


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
        if len(group) > 1:
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


class GroupRepo(object):

    # class variable
    filter_out = ["root", "nogroup"]

    def __init__(self, store_file=None):
        self.store_file = store_file
        if self.store_file == None:
            self.store_file = os.path.join("~", ".grpinfo")
        self.store_file = os.path.expanduser(self.store_file)
        self.groups = []
        self.gmap = {}
        self.gmap_keys = []

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + " store: '"
            + self.store_file
            + "'"
            + " groups: "
            + str(len(self.groups))
            + " )"
        )

    def read_current(self):
        all_grps = grp.getgrall()
        self.groups = map(lambda x: Group().from_grp(x), all_grps)
        self._init_internal()
        return self

    def _init_internal(self):
        self.groups = sorted(self.groups, key=lambda x: x.name)

        if len(self.filter_out) > 0:
            self.groups = list(
                filter(lambda x: x.name not in self.filter_out, self.groups)
            )

        self.gmap = dict(map(lambda x: (x.name, x), self.groups))
        self.gmap_keys = sorted(self.gmap.keys())
        return self

    def from_store(self):
        with open(self.store_file) as f:
            lines = f.readlines()
        lines = map(lambda x: x.strip(), lines)
        lines = filter(lambda x: len(x) > 0, lines)
        lines = list(filter(lambda x: x.find("#") != 0, lines))
        self.groups = []
        for line in lines:
            g = Group().loads(line)
            self.groups.append(g)
        self._init_internal()
        return self

    def write_store(self):
        with open(self.store_file, "w") as f:
            f.write("#group <tab> user list (comma separated)\n\n")
            for g in self.groups:
                f.write(g.dumps())
                f.write("\n")

    def where_used(self, search_for):
        return list(
            filter(
                lambda x: x.name == search_for or search_for in x.member, self.groups
            )
        )

    def find(self, search_for):
        return self.gmap[search_for]

    def list_all(self):
        return self.groups

    def list_no_member(self):
        return list(filter(lambda x: len(x.member) == 0, self.groups))

    def list_with_member(self):
        return list(filter(lambda x: len(x.member) > 0, self.groups))

    def list_hierachy(self):
        hierarchy = []
        found = set()
        remaining = list(map(lambda x: x.name, self.groups))
        while len(remaining) > 0:
            old_size = len(remaining)
            for g in remaining:
                m = set(self.gmap[g].member)
                if len(m) == 0 or m.issubset(found):
                    found.add(g)
                    hierarchy.append(g)
                    remaining.remove(g)
                    # break here to keep result somehow sorted
                    break
            if old_size == len(remaining):
                raise Exception("found cycle in group definition")
        return list(map(lambda x: self.gmap[x], hierarchy))


def dumps(grplist, full=True, hide_name=False, show_multiline=False):
    for g in grplist:
        if full:
            print(g.dumps())
        else:
            if hide_name == True:
                if len(g.member) == 0:
                    return
                if show_multiline == True:
                    [print(m) for m in g.member]
                else:
                    print(",".join(g.member))
            else:
                print(g.name)
