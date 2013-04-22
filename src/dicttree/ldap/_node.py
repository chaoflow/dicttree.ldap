import copy
import ldap

from dicttree.ldap import scope


try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class Attributes(object):
    @property
    def ldap(self):
        return self.node.ldap

    def __init__(self, dn=None, attrs=(), node=None):
        self.dn = dn
        self.attrs = OrderedDict(attrs)
        self.node = node

    def __contains__(self, name):
        entry = self.ldap.search_s(self.dn, scope.BASE,
                                    attrlist=[name], attrsonly=True)[0]
        return len(entry[1]) > 0

    def __getitem__(self, name):
        entry = self.ldap.search_s(self.dn, scope.BASE,
                                    attrlist=[name])[0]
        return entry[1][name]

    def __setitem__(self, name, value):
        action = ldap.MOD_ADD
        if name in self:
            action = ldap.MOD_REPLACE
        self.ldap.modify_s(self.dn, [(action, name, value)])

    def __delitem__(self, name, value=None):
        """ delete attibutes value, if value is None
        deletes all values for given attribute name """
        self.ldap.modify_s(self.dn, [(ldap.MOD_DELETE, name, value)])

    def __iter__(self):
        return (item[0] for item in self._search())

    def _search(self, attrlist=None):
        """ldap search returning a generator on attributes
        """
        entry = self.ldap.search_s(self.dn, scope.BASE, attrlist=attrlist)
        for name in entry[0][1]:
            yield (name, entry[0][1][name])

    def __len__(self):
        return sum(1 for x in iter(self))

    def __eq__(self, other):
        # XXX quick fix, for old test cases
        return dict(self.attrs).items() == dict(other.attrs).items()

    def keys(self):
        return iter(self)

    def values(self):
        return (item[1] for item in self._search())

    def items(self):
        res = dict(self.attrs).items()
        #res2 = [(item[0], item[1]) for item in self._search()]
        #res = [('objectClass', ['organizationalRole']), ('cn', ['cn0'])]
        #ipdb.set_trace()
        return res

#    def clear(self):
#        for name in self.keys():
#            del self[name]

    def copy(self):
        return copy.copy(self.attrs)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def pop(self, name, default=None):
        try:
            value = self[name]
            del self[name]
        except KeyError:
            if default is None:
                raise KeyError(name)
            return default
        return value

#    def popitem(self):
#        if not self:
#          raise KeyError
#        dn = next(iter(self))
#        node = self[dn]
#        del self[dn]
#        return (dn, node)

    def setdefault(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            self[name] = default
            return default

    def update(self, other):
        try:
            items = other.items()
        except AttributeError:
            items = other
        for name, value in items:
            self[name] = value
        return None


class CachedAttributes(Attributes):
    def __getitem__(self, key):
        try:
            value = self.attrs[key]
        except KeyError:
            _next = super(CachedAttributes, self).__getitem__
            value = _next(key)
            self.attrs[key] = value
        return value

    def __delitem__(self, key):
        try:
            del self.attrs[key]
        except KeyError:
            pass
        _next = super(CachedAttributes, self).__delitem__
        _next(key)

    def __contains__(self, key):
        try:
            value = key in self.attrs
        except KeyError:
            _next = super(CachedAttributes, self).__contains__
            value = _next(key)
        return value

    def __setitem__(self, key, value):
        _next = super(CachedAttributes, self).__setitem__
        _next(key, value)
        self.attrs[key] = value


class Node(object):
    @property
    def ldap(self):
        return self.directory.ldap

    def __init__(self, name=None, attrs=(), directory=None):
        self.name = name
        # python-ldap uses (unordered) dicts to return attributes. I
        # am under the impression that openldap preserves attribute
        # order from an ldif file, which would mean patching
        # python-ldap would give us order. Needs to be investigated.
        #self.attrs = OrderedDict(attrs)
        self.attrs = CachedAttributes(dn=name, attrs=attrs, node=self)
        self.directory = directory

    def __eq__(self, other):
        return self is other or \
            self.name == other.name and \
            self.attrs == other.attrs

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<ldap node dn="%s">' % (self.name,)

    def iteritems(self):
        return iter([])

    def __contains__(self, key):
        return key in self.attrs

    def __getitem__(self, key):
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __delitem__(self, key):
        del self.attrs[key]
