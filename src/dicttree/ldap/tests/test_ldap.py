import ldap
import unittest

from itertools import chain

from dicttree.ldap import Directory
from dicttree.ldap import Node
from dicttree.ldap.tests import mixins


class TestLDAPDirectory(mixins.Slapd, unittest.TestCase):
    ENTRIES = {
        'cn=cn0,o=o': (('cn', ['cn0']),
                       ('objectClass', ['organizationalRole'])),
        'cn=cn1,o=o': (('cn', 'cn1'),
                       ('objectClass', ['organizationalRole'])),
        }
    ADDITIONAL = {
        'cn=cn2,o=o': (('cn', ['cn2']),
                       ('objectClass', ['organizationalRole'])),
        }

    def test_contains(self):
        self.assertTrue('cn=cn0,o=o' in self.dir)
        self.assertFalse('cn=fail,o=o' in self.dir)

    def test_getitem(self):
        def get_nonexistent():
            self.dir['cn=fail,o=o']

        dn = 'cn=cn0,o=o'
        self.assertEqual(self.dir[dn], self.dir[dn])
        self.assertEqual(dn, self.dir[dn].name)
        # (currently) order is not preserved, see dicttree.ldap.Node
        #self.assertEqual(self.ENTRIES[dn], tuple(self.dir[dn].attrs.items()))
        self.assertItemsEqual(self.ENTRIES[dn], self.dir[dn].attrs.items())
        self.assertRaises(KeyError, get_nonexistent)

    def test_setitem(self):
        dn = 'cn=cn2,o=o'
        node = Node(name=dn, attrs=self.ADDITIONAL[dn])
        def addnode():
            self.dir[dn] = node

        addnode()
        self.assertRaises(KeyError, addnode)
        self.assertEquals(node, self.dir[dn])

    def test_delitem(self):
        def delete():
            del self.dir['cn=cn0,o=o']

        def search_deleted():
            self.ldap.search_s('cn=cn0,o=o', ldap.SCOPE_BASE)

        delete()
        self.assertRaises(KeyError, delete)
        self.assertRaises(ldap.NO_SUCH_OBJECT, search_deleted)

    def test_iter(self):
        self.assertItemsEqual(self.ENTRIES.keys(), self.dir)

    def test_keys(self):
        self.assertItemsEqual(self.ENTRIES.keys(), self.dir.keys())

    def test_values(self):
        self.assertItemsEqual(self.ENTRIES.keys(),
                              (node.name for node in self.dir.values()))

    def test_items(self):
        self.assertItemsEqual(((dn, dn) for dn in self.ENTRIES.keys()),
                              ((dn, node.name) for dn, node in self.dir.items()))
