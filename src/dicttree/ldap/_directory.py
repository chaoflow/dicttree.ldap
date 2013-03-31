import ldap

from ldap import SCOPE_BASE
from ldap import SCOPE_ONELEVEL
from ldap import SCOPE_SUBTREE
from ldap.ldapobject import LDAPObject

from dicttree.ldap._node import Node
from dicttree.ldap._views import KeysView
from dicttree.ldap._views import ItemsView
from dicttree.ldap._views import ValuesView

import copy

class Directory(object):
    """XXX: this could be without base_dn, not supporting iteration
    """
    def __init__(self, uri, base_dn, bind_dn, pw):
        self.base_dn = base_dn
        self._ldap = LDAPObject(uri)
        self._ldap.bind_s(bind_dn, pw)

    def __contains__(self, dn):
        try:
            return dn == self._ldap.search_s(dn, SCOPE_BASE,
                                             attrlist=[''])[0][0]
        except ldap.NO_SUCH_OBJECT:
            return False

    def __getitem__(self, dn):
        try:
            entry = self._ldap.search_s(dn, SCOPE_BASE)[0]
        except ldap.NO_SUCH_OBJECT:
            raise KeyError(dn)
        node = Node(name=dn, attrs=entry[1], ldap=self._ldap)
        return node

    def __setitem__(self, dn, node):
        addlist = node.attrs.items()
        try:
            self._ldap.add_s(dn, addlist)
        except ldap.ALREADY_EXISTS:
            del self[dn]
            self._ldap.add_s(dn, addlist)

    def __delitem__(self, dn):
        try:
            self._ldap.delete_s(dn)
        except ldap.NO_SUCH_OBJECT:
            raise KeyError(dn)

    def __iter__(self):
        return (x[0][0] for x in
                self._search(self.base_dn, SCOPE_SUBTREE)
                if x[0][0] != self.base_dn)

    def _search(self, base, scope, filterstr='(objectClass=*)', attrlist=None,
                timeout=-1):
        """asynchronous ldap search returning a generator
        """
        msgid = self._ldap.search(base, scope,
                                  filterstr=filterstr, attrlist=attrlist)
        rtype = ldap.RES_SEARCH_ENTRY
        while rtype is ldap.RES_SEARCH_ENTRY:
            # Fetch results single file, the final result (usually)
            # has an empty field. <sigh>
            (rtype, data) = self._ldap.result(msgid=msgid, all=0,
                                              timeout=timeout)
            if rtype is ldap.RES_SEARCH_ENTRY or data:
                yield data

    def items(self):
        return ItemsView(directory=self)

    def keys(self):
        return KeysView(directory=self)

    def values(self):
        return ValuesView(directory=self)

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
        node = self[dn]
        del self[dn]
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
        return (Node(name=x[0][0], attrs=x[0][1], ldap=self._ldap) for x in
                self._search(self.base_dn,
                                  ldap.SCOPE_SUBTREE, attrlist=[''])
                if x[0][0] != self.base_dn)

    def iteritems(self):
        return ((node.name, node) for node in ValuesView(self))
