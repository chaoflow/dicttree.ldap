import itertools
import collections

class DirView(object):
    def __init__(self, directory):
        self.directory = directory

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

class DirViewSet(DirView, collections.Set):
    def _from_iterable(self, iterable):
        return set(iterable)

class ItemsView(DirViewSet):
    def __iter__(self):
        return self.directory.iteritems()

class KeysView(DirViewSet):
    def __iter__(self):
        return iter(self.directory)

class ValuesView(DirView):
    def __iter__(self):
        return self.directory.itervalues()
