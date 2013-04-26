from metachao import aspect
from metachao.aspect import Aspect

from ldap import SCOPE_BASE
from ldap import SCOPE_SUBTREE

from dicttree.ldap._node import Node

import ipdb

class entryUUID(Aspect):
    """
    Use user entryUUID from LDAP as dn
    ----------------------------------
    """

    def get_dn(self, entryUUID):
        lookup = self.ldap.search_s(base="o=o", scope=SCOPE_SUBTREE,
                                    filterstr='entryUUID='+entryUUID,
                                    attrlist=[''])
        return lookup[0][0]

    @aspect.plumb
    def __getitem__(_next, self, entryUUID):
        # get the uuid for test -> remove this!!!
        #lookup = self.ldap.search_s(base=dn, scope=SCOPE_BASE,
        #                            attrlist=['entryUUID'])[0]
        #entryUUID =  lookup[1]['entryUUID'][0]
        dn = self.get_dn(entryUUID)
        node = _next(dn)
        node.name = entryUUID
        node['cn'] = entryUUID
        return node


class identifyDN(Aspect):

    def __init__(self, idattr):
        self.idattr = idattr
        super(Aspect, self).__init__()

    def get_dn(self, id):
        dn = self.idattr + "="+ id + ',' + self.ldap.base_dn
        return dn

    @aspect.plumb
    def __getitem__(_next, self, id):
        node = _next(self.get_dn(id))
        node.name = id
        return node


class attrmapper(Aspect):

    MAPPING_IN = {
        "description": 'userPassword'
    }

    MAPPING_OUT = {
        "userPassword": 'description'
    }

    def mappattr(self, attr, direction='in'):
        MAPPING = self.MAPPING_IN
        if direction != 'in':
            MAPPING = self.MAPPING_OUT
        if attr in MAPPING:
           return MAPPING[attr]
        return attr

    def mappdn(self, dn, direction='in'):
        index = dn.find('=')
        attr = dn[:index]
        return self.mappattr(attr, direction) + dn[index:]

    def mappattrsdict(self, attrs, direction='in'):
        #ipdb.set_trace()
        for key in attrs.keys():
            mappedkey = self.mappattr(key, direction)
            if key != mappedkey:
                attrs[mappedkey] = attrs[key]
                del attrs[key]
        return attrs

    def mappnode(self, node, direction='in'):
        node.name = self.mappdn(node.name, direction)
        node.attrs = self.mappattrsdict(node.attrs, direction)
        return node

    #@aspect.plumb
    #def __getitem__(_next, self, dn):
    #    dn = self.mappdn(dn)
    #    node = _next(dn)
    #    node = self.mappnode(node, 'out')
    #    return node

    @aspect.plumb
    def __setitem__(_next, self, dn, node):
        dn = self.mappdn(dn)
        node = self.mappnode(node)
        _next(dn, node)

    @aspect.plumb
    def __delitem__(_next, self, dn):
        dn = self.mappdn(dn)
        _next(dn)

    @aspect.plumb
    def __contains__(_next, self, dn):
        dn = self.mappdn(dn)
        return _next(dn)

    #@aspect.plumb
    #def get(_next, self, dn, default=None):
    #    dn = self.mappdn(dn)
    #    result = _next(dn, default)
    #    if isinstance(result, Node):
    #        return self.mappnode(result, 'out')
    #    return default

    #@aspect.plumb
    #def pop(_next, self, dn, default=None):
    #    dn = self.mappdn(dn)
    #    result = _next(dn, default)
    #    if isinstance(result, Node):
    #        return self.mappnode(result, 'out')
    #    return default

    @aspect.plumb
    def popitem(_next, self):
        result = _next()
        return (self.mappdn(result[0], 'out'), self.mappnode(result[0], 'out'))

    @aspect.plumb
    def setdefault(_next, self, dn, default=None):
        dn = self.mappdn(dn)
        node = _next(dn, default)
        return self.mappnode(result, 'out')

    #@aspect.plumb
    #def update(_next, self, other):

    #@aspect.plumb
    #def __iter__(_next, self):
    #    pass
    #XXX wrap search for iter?
    #check also for keys, values, items!

    #@aspect.plumb
    #def _search(_next, self, base=None, scope=SUBTREE,
    #            filterstr=None, attrlist=None, timeout=10):
        #XXX mapp filterstr and attrlist
