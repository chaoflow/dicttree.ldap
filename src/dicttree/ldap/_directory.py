import copy
import ldap

from pyldap import PyReconnectLDAPObject

from dicttree.ldap import scope
from dicttree.ldap._node import Node
from dicttree.ldap._views import KeysView
from dicttree.ldap._views import ItemsView
from dicttree.ldap._views import ValuesView


class Directory(object):
    """XXX: this could be without base_dn, not supporting iteration
    """
    Node = Node
    _ldap = None

    @property
    def ldap(self):
        if self._ldap is not None:
            if self._ldap.whoami_s() == '':
                del self._ldap
        if self._ldap is None:
            self._ldap = PyReconnectLDAPObject(self.uri)
            self._ldap.bind_s(self.bind_dn, self.bind_pw)
        return self._ldap

    def __init__(self, uri=None, base_dn=None, bind_dn=None, bind_pw=None):
        self.base_dn = base_dn
        self.uri = uri
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw

    def __contains__(self, dn):
        try:
            return dn == self.ldap.search_s(dn, scope.BASE,
                                             attrlist=[''])[0][0]
        except ldap.NO_SUCH_OBJECT:
            return False

    def __getitem__(self, dn):
        try:
            entry = self.ldap.search_s(dn, scope.BASE)[0]
        except ldap.NO_SUCH_OBJECT:
            raise KeyError(dn)
        node = self.Node(name=dn, attrs=entry[1], directory=self)
        return node

    def __setitem__(self, dn, node):
        addlist = node.attrs.items()
        try:
            self.ldap.add_s(dn, addlist)
        except ldap.ALREADY_EXISTS:
            del self[dn]
            self.ldap.add_s(dn, addlist)

    def __delitem__(self, dn):
        try:
            self.ldap.delete_s(dn)
        except ldap.NO_SUCH_OBJECT:
            raise KeyError(dn)

    def __iter__(self):
        return (x[0] for x in self._search())

    def _search(self, base=None, scope=scope.SUBTREE,
                filterstr=None, attrlist=None,
                timeout=10):
        """asynchronous ldap search returning a generator
        """
        base = base or self.base_dn
        filterstr = str(filterstr or '(objectClass=*)')
        return [x for x in
                self.ldap.search_s(base=base, scope=scope,
                                   filterstr=filterstr, attrlist=attrlist)
                if x[0] != self.base_dn
        ]

    def _search_async(self, base=None, scope=scope.SUBTREE,
                filterstr=None, attrlist=None,
                timeout=10):
        """asynchronous ldap search returning a generator
        """
        base = base or self.base_dn
        filterstr = str(filterstr or '(objectClass=*)')
        try:
            msgid = self.ldap.search(base=base, scope=scope,
                                  filterstr=filterstr, attrlist=attrlist)
        except ldap.SERVER_DOWN:
            # Just retry once
            del self._ldap
            msgid = self.ldap.search(base=base, scope=scope,
                                  filterstr=filterstr, attrlist=attrlist)
        rtype = ldap.RES_SEARCH_ENTRY
        while rtype is ldap.RES_SEARCH_ENTRY:
            # Fetch results single file, the final result (usually)
            # has an empty field. <sigh>
            (rtype, data) = self.ldap.result(msgid=msgid, all=0,
                                              timeout=timeout)
            if rtype is ldap.RES_SEARCH_ENTRY or data:
                if data[0][0] != self.base_dn:
                    yield data

    def items(self):
        return ItemsView(self)

    def keys(self):
        return KeysView(self)

    def values(self):
        return ValuesView(self)

    def __len__(self):
        return sum(1 for node in iter(self))

    def clear(self):
        for dn in self.keys():
            del self[dn]

    def copy(self):
        return copy.copy(self)

    def get(self, dn, default=None):
        try:
            return self[dn]
        except KeyError:
            return default

    def pop(self, dn, default=None):
        try:
            node = self[dn]
            del self[dn]
        except KeyError:
            if default is None:
                raise KeyError(dn)
            return default
        return node

    def popitem(self):
        if not self:
            raise KeyError
        dn = next(iter(self))
        node = self.pop(dn)
        return (dn, node)

    def setdefault(self, dn, default=None):
        try:
            return self[dn]
        except KeyError:
            self[default.name] = default
            return default

    def update(self, other):
        try:
            items = other.items()
        except AttributeError:
            items = other
        for dn, node in items:
            self[dn] = node
        return None

    iterkeys = __iter__

    def itervalues(self):
        return (self.Node(name=x[0], attrs=x[1], directory=self) for x in
                self._search(scope=scope.SUBTREE, attrlist=['']))

    def iteritems(self):
        return ((node.name, node) for node in self.itervalues())

    def add(self, addlist):
        #XXX determine dn?
        self.ldap.add_s(dn, addlist)
