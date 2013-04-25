from metachao import aspect
from metachao.aspect import Aspect

from ldap import SCOPE_BASE
from ldap import SCOPE_SUBTREE

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

class identify(Aspect):
    pass
