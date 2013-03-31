import unittest

from ldap import UNDEFINED_TYPE
from ldap import PROTOCOL_ERROR
from dicttree.ldap.tests import mixins
from dicttree.ldap._node import Attributes

class TestNodeAttrs(mixins.Slapd, unittest.TestCase):
    ENTRIES = {
        'cn=cn0,o=o': (('objectClass', ['organizationalRole']),
                       ('cn', ['cn0'])),
        'cn=cn1,o=o': (('objectClass', ['organizationalRole']),
                       ('cn', ['cn1']))
    }

    def test_getitem(self):
        node = self.dir['cn=cn0,o=o']
        self.assertEqual(node.attrs['cn'], ['cn0'])
        self.assertEqual(node.attrs['objectClass'], ['organizationalRole'])
        def fail():
            node.attrs['fail']
        self.assertRaises(KeyError, fail)

    def test_contains(self):
        node = self.dir['cn=cn0,o=o']
        self.assertTrue('cn' in node.attrs)
        self.assertTrue('objectClass' in node.attrs)
        self.assertFalse('fail' in node.attrs)

    def test_iter(self):
        node = self.dir['cn=cn0,o=o']
        self.assertItemsEqual(node.attrs, ['objectClass', 'cn'])

    def test_del(self):
        node = self.dir['cn=cn0,o=o']
        node.attrs['description'] = 'abc'
        self.assertItemsEqual(node.attrs, ['objectClass', 'cn', 'description'])
        del node.attrs['description']
        self.assertItemsEqual(node.attrs, ['objectClass', 'cn'])

    def test_len(self):
        node = self.dir['cn=cn0,o=o']
        self.assertEqual(len(node.attrs), 2)

    def test_setitem(self):
        node = self.dir['cn=cn0,o=o']
        node.attrs['description'] = 'abc'
        self.assertEqual(len(node.attrs), 3)
        self.assertEqual(node.attrs['description'], ['abc'])
        self.assertItemsEqual(node.attrs, ['objectClass', 'cn', 'description'])
        node.attrs['description'] = 'aaa'
        self.assertEqual(node.attrs['description'], ['aaa'])

    def test_equal(self):
        pass
        #XXX create test after implementing items method

    def test_keys(self):
        node = self.dir['cn=cn0,o=o']
        self.assertItemsEqual(dict(self.ENTRIES['cn=cn0,o=o']).keys(),
                              node.attrs.keys())

    def test_values(self):
        node = self.dir['cn=cn0,o=o']
        self.assertItemsEqual(dict(self.ENTRIES['cn=cn0,o=o']).values(),
                              node.attrs.values())

    def test_items(self):
        node = self.dir['cn=cn0,o=o']
        self.assertEqual(dict(self.ENTRIES['cn=cn0,o=o']).items(),
                              node.attrs.items())

    def test_copy(self):
        node = self.dir['cn=cn0,o=o']
        copy = node.attrs.copy()
        #XXX use Attributes object instead of dict
        self.assertEqual(dict(self.ENTRIES['cn=cn0,o=o']), copy)

    def test_get(self):
        node = self.dir['cn=cn0,o=o']
        self.assertEqual(node.attrs.get('cn'), ['cn0'])
        self.assertEqual(node.attrs.get('fail', 'default'), 'default')
        self.assertEqual(node.attrs.get('fail'), None)

    def test_pop(self):
        node = self.dir['cn=cn0,o=o']
        node.attrs['description'] = 'abc'
        self.assertEqual(['abc'], node.attrs.pop('description'))
        self.assertFalse('description' in node.attrs)
        self.assertEqual('default', node.attrs.pop('fail', 'default'))
        self.assertRaises(KeyError, lambda: node.attrs.pop('fail'))

    def test_setdefault(self):
        node = self.dir['cn=cn0,o=o']
        self.assertEqual(['cn0'], node.attrs.setdefault('cn'))
        self.assertEqual('abc', node.attrs.setdefault('description', 'abc'))
        self.assertRaises(UNDEFINED_TYPE,
                          lambda: node.attrs.setdefault('fail', 'fail'))
        self.assertRaises(PROTOCOL_ERROR,
                          lambda: node.attrs.setdefault('fail'))

    def test_update(self):
        node = self.dir['cn=cn0,o=o']
        attrs = Attributes('cn=cn0,o=o', self.ENTRIES['cn=cn0,o=o'])
        node.attrs.update(attrs)
        self.assertEqual(node.attrs, attrs)
        node.attrs.update((('objectClass', ['organizationalRole']),
                           ('cn', ['cn0']), ('description', ['abc'])))
        self.assertEqual(['abc'], node.attrs.pop('description'))
        self.assertEqual(node.attrs, attrs)
