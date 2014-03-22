from collections import defaultdict, Mapping
import json


class SetterDict(defaultdict):
    """
    A recursive defaultdict with extra bells & whistles

    It enables you to set keys at any depth without first creating the
    intermediate levels, e.g.

      d = SetterDict()
      d["a"]["b"]["c"] = 1

    It also allows access using normal getattr syntax, interchangeably:

      d.a["b"].c == d.a.b.c == d["a"]["b"]["c"]

    Note: only allows string keys for now.
    """

    def __init__(self, value={}, factory=None):
        factory = factory or SetterDict
        defaultdict.__init__(self, factory)
        for k, v in value.items():
            if isinstance(v, Mapping):
                SetterDict.__setitem__(self, k, factory(v))
            else:
                SetterDict.__setitem__(self, k, v)

    def __setattr__(self, attr, value):
        self[attr] = value

    def __getattr__(self, attr):
        return self[attr]

    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, json.dumps(self))


def merge(d, u):
    "Recursively 'merge' a Mapping into another"
    for k, v in u.iteritems():
        if isinstance(v, Mapping):
            merge(d[k], v)
        elif isinstance(d, Mapping):
            d[k] = u[k]


class AppendingDict(SetterDict):

    """An extra weird SetterDict where assignment adds items instead of
    overwriting. It also allows setting nested values using dicts (or
    any Mapping). Plus of course the features of SetterDict.

    a = AppendingDict()
    a.b = 1
    a.b
    -> 1
    a.b = 2
    a.b
    -> [1, 2]

    a = AppendingDict()
    a.b.c.d = 3
    a.b = {"c": {"d": 4}}
    a
    -> {"b": {"c": {"d": [3, 4]}}}

    """

    def __init__(self, value={}):
        SetterDict.__init__(self, value, AppendingDict)

    def __setitem__(self, attr, value):
        # I apologize for this method :(
        if attr in self:
            if isinstance(self[attr], AppendingDict):
                if isinstance(value, Mapping):
                    merge(self[attr], value)
                else:
                    SetterDict.__setitem__(self, attr, value)
            elif isinstance(self[attr], list):
                self[attr].append(value)
            else:
                SetterDict.__setitem__(self, attr, [self[attr]])
                self[attr].append(value)
        else:
            if (isinstance(value, Mapping) and
                not isinstance(value, AppendingDict)):
                SetterDict.__setitem__(self, attr, AppendingDict(value))
            else:
                SetterDict.__setitem__(self, attr, value)
