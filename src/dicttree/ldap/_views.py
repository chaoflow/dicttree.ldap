import collections
import itertools


class DictView(object):
    def __init__(self, dct):
        self.dct = dct

    def __contains__(self, other):
        for x in self:
            if other == x:
                return True
        return False

    def __len__(self):
        return sum(1 for x in iter(self))

    def __eq__(self, other):
        if self is other:
            return True
        if len(self) != len(other):
            return False
        for x, x2 in itertools.izip(self, other):
            if x != x2:
                return False
        return True

    def __ne__(self, other):
        return not self == other


class ValuesView(DictView):
    def __iter__(self):
        return self.dct.itervalues()


class SetLikeDictView(DictView, collections.Set):
    def _from_iterable(self, iterable):
        return set(iterable)


class ItemsView(SetLikeDictView):
    def __iter__(self):
        return self.dct.iteritems()


class KeysView(SetLikeDictView):
    def __iter__(self):
        return iter(self.dct)
