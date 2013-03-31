import ldap
import unittest

from dicttree.ldap._node import Node
from dicttree.ldap._views import KeysView
from dicttree.ldap._views import ItemsView
from dicttree.ldap.tests import mixins


#XXX remove imports
import collections
import ipdb


class TestKeysView(mixins.Slapd, unittest.TestCase):
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

    def test_viewlen(self):
        def delete():
            del self.dir['cn=cn0,o=o']

        dn1 = 'cn=cn0,o=o'
        node1 = Node(name=dn1, attrs=self.ENTRIES[dn1])
        def addnode1():
            self.dir[dn1] = node1

        dn2 = 'cn=cn2,o=o'
        node2 = Node(name=dn2, attrs=self.ADDITIONAL[dn2])
        def addnode2():
            self.dir[dn2] = node2

        self.assertEqual(len(self.ENTRIES.keys()), len(self.dir.keys()))
        delete()
        self.assertTrue(len(self.ENTRIES.keys()) > len(self.dir.keys()))
        addnode1()
        addnode2()
        self.assertTrue(len(self.ENTRIES.keys()) < len(self.dir.keys()))

    def test_viewequal(self):
        keys = self.dir.keys()
        self.assertTrue(keys == keys)
        self.assertTrue(self.ENTRIES.keys() == keys)
        self.assertFalse(self.ENTRIES.keys() != keys)

        del self.dir['cn=cn0,o=o']
        keys= self.dir.keys()
        items = self.dir.items()
        values = self.dir.values()
        self.assertTrue(self.ENTRIES.keys() != keys)

    def test_notequal(self):
        dn='cn=cn0, o=o'
        fail='cn=fail,o=o'
        keysList = [dn, fail]
        keys = self.dir.keys()
        self.assertTrue(keys != keysList)

    def test_viewcontains(self):
        dn = 'cn=cn0,o=o'
        fail = 'cn=fail, o=o'
        keys = self.dir.keys()

        self.assertTrue(dn in keys)
        self.assertFalse(fail in keys)

    def test_and(self):
        keys = self.dir.keys()
        andKeys = keys & keys
        self.assertEqual(keys, andKeys)
        self.assertTrue(keys == andKeys)

    def test_or(self):
        keysList = ['cn=cn0,o=o', 'cn=cn2,o=o']
        keysResult = set(['cn=cn0,o=o', 'cn=cn1,o=o', 'cn=cn2,o=o'])
        keys = self.dir.keys()
        orKeys = keys | keysList
        self.assertTrue(orKeys == keysResult)

    def test_xor(self):
        dn2 = 'cn=cn2,o=o'
        testKeys = KeysView(directory=self.ENTRIES)
        keysResult = set([dn2])
        self.dir[dn2] = Node(name=dn2, attrs=self.ADDITIONAL[dn2])

        keys = self.dir.keys()
        xorKeys = keys ^ keys
        self.assertEqual(set(), xorKeys)

        keys = self.dir.keys()
        xorKeys = keys ^ testKeys
        self.assertEqual(xorKeys, keysResult)

    def test_sub(self):
        dn2 = 'cn=cn2,o=o'
        self.dir[dn2] = Node(name=dn2, attrs=self.ADDITIONAL[dn2])
        testKeys = KeysView(directory=self.ENTRIES)
        keysResult = set([dn2])

        keys = self.dir.keys()
        subKeys = keys - keys
        self.assertEqual(set(), subKeys)

        subKeys = keys - testKeys
        self.assertEqual(keysResult, subKeys)

    def test_isdisjoint(self):
        keys = self.dir.keys()
        testKeys = KeysView(directory=self.ADDITIONAL)

        self.assertFalse(keys.isdisjoint(keys))
        self.assertTrue(keys.isdisjoint(testKeys))



class TestItemsView(mixins.Slapd, unittest.TestCase):
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

    def test_viewlen(self):
        def delete():
            del self.dir['cn=cn0,o=o']

        dn1 = 'cn=cn0,o=o'
        node1 = Node(name=dn1, attrs=self.ENTRIES[dn1])
        def addnode1():
            self.dir[dn1] = node1

        dn2 = 'cn=cn2,o=o'
        node2 = Node(name=dn2, attrs=self.ADDITIONAL[dn2])
        def addnode2():
            self.dir[dn2] = node2

        self.assertEqual(len(self.ENTRIES.items()), len(self.dir.items()))
        delete()
        self.assertTrue(len(self.ENTRIES.items()) > len(self.dir.items()))
        addnode1()
        addnode2()
        self.assertTrue(len(self.ENTRIES.items()) < len(self.dir.items()))

    def test_viewequal(self):
        dn = 'cn=cn0,o=o'
        node = Node(name=dn)
        dn1 = 'cn=cn1,o=o'
        node1 = Node(name=dn1)
        itemsList = [(dn, node), (dn1, node1)]

        items = self.dir.items()
        self.assertTrue(items == items)
        self.assertTrue(items == itemsList)
        self.assertFalse(items != itemsList)

        del self.dir['cn=cn0,o=o']
        items = self.dir.items()
        self.assertTrue(self.ENTRIES.items() != items)

    def test_notequal(self):
        dn='cn=cn0, o=o'
        node=Node(name=dn)
        fail='cn=fail,o=o'
        node1=Node(name=fail)
        itemsList = [(dn, node),(fail, node1)]
        items = self.dir.items()

        self.assertTrue(items != itemsList)

    def test_viewcontains(self):
        dn = 'cn=cn0,o=o'
        node = Node(name=dn)
        item = (dn, node)
        fail = 'cn=fail, o=o'
        failNode = Node(name=fail)
        failItem = (fail, failNode)
        items = self.dir.items()

        self.assertTrue(item in items)
        self.assertFalse(failItem in items)

    def test_and(self):
        # and returns elements that overlaps in both sets
        # or returns all elements but overlaping only once
        # xor returns all elements except the overlaping
        # sub returns all elements of first set except overlaping
        # isdisjoint any two disjoint sets are not equal
        #           and are not subsets of each other,
        #           so all of the following return False: a<b, a==b, or a>b
       # s1 = ListBasedSet('abcdd')
       # s2 = ListBasedSet('ddefg')
       # test = s1 | s2
       # k = ''
       # for x in test:
       #     k += x
       # self.assertFalse(k)

        items = self.dir.items()
        andItems = items & items
        #XXX andItems has reversed element positions
        # self.assertTrue(items == andItems)

    def test_or(self):
        dn = 'cn=cn0,o=o'
        dn1 = 'cn=cn1,o=o'
        dn2 = 'cn=cn2,o=o'
        itemsList = ((dn, Node(name=dn)), (dn2, Node(name=dn2)))
        itemsResult = set([(dn, Node(name=dn)), (dn1, Node(name=dn1)),
                           (dn2, Node(name=dn2))])
        items = self.dir.items()
        orItems = items | itemsList
        # XXX or uses chain and concats all elements for items ?!?
        #self.assertTrue(orItems == itemsResult)

    def test_xor(self):
        dn2 = 'cn=cn2,o=o'
        testKeys = KeysView(directory=self.ENTRIES)
        mockDir = MockDirectory(self.ENTRIES)
        mockDir.base_dn = ''
        testItems = ItemsView(directory=mockDir)
        itemsResult = set([(dn2, Node(name=dn2))])
        self.dir[dn2] = Node(name=dn2, attrs=self.ADDITIONAL[dn2])

        #items = self.dir.items()
        #xorItems = items ^ items
        #self.assertEqual(set(), xorItems)

        #ipdb.set_trace()
        #xorItems = items ^ testItems
        #self.assertEqual(xorItems, itemsResult)

    def test_sub(self):
        dn2 = 'cn=cn2,o=o'
        self.dir[dn2] = Node(name=dn2, attrs=self.ADDITIONAL[dn2])
        #mockDir = MockDirectory({'a': (('a1', ['x1']),
        #                               ('aa1', ['xx1'])),
        #                         'b': (('b1', ['y1']),
        #                               ('bb1', ['yy1']))
        #                     })

        mockDir = MockDirectory(self.ENTRIES)
        mockDir.base_dn = ''
        testItems = ItemsView(directory=mockDir)
        #mockDir2 = MockDirectory({'a': (('a1', ['x1']),
        #                                ('aa1', ['xx1']))})
        mockDir2 = MockDirectory(self.ENTRIES)
        mockDir2.base_dn = ''
        testItems2 = ItemsView(directory=mockDir2)

        dn1 = 'cn=cn1,o=o'
        #itemsResult = set([(dn1,
        #                    Node(name=dn1,
        #                         attrs=
        #                         {'objectClass': ['organizationalRole'],
        #                          'cn': dn1}))])

        items = self.dir.items()
        subItems = items - items
        self.assertEqual(set(), subItems)

        #del mockDir2[dn1]
        #del mockDir2['a']
        #subItems = testItems - testItems2
        #ipdb.set_trace()
        #self.assertEqual(subItems, set([('b', Node(name='b'))]))

        #XXX even as nodes are equal, sets are not equal
        # using assertSetEqual func,  see s1, s2

        #item = iter(subItems).next()
        #node = item[1]
        #setFromView = set([(item[0], item[1])])
        #node2 = Node(name=dn1,attrs=
        #             {'objectClass': ['organizationalRole'],
        #              'cn': 'cn1'})
        #ipdb.set_trace()
        #self.assertEqual(node, node2)
        #self.assertEqual(item[0], dn1)
        #self.assertEqual(setFromView, itemsResult)
        #ipdb.set_trace()
        #self.assertEqual(subItems, itemsResult)

        #s1 = set([node])
        #s2 = set([node2])
        #self.assertEqual(s1, s2)

        #XXX unable to test against nodes as attributes required to
        #simulate search results and no attrs are returned from ldap
        #subItems = items - testItems
        #self.assertEqual(subItems, itemsResult)

    def test_isdisjoint(self):
        items = self.dir.items()
        mockDir = MockDirectory(self.ADDITIONAL)
        mockDir.base_dn = ''
        testItems = ItemsView(directory=mockDir)

        self.assertFalse(items.isdisjoint(items))
        self.assertTrue(items.isdisjoint(testItems))

class MockDirectory(dict):
    def _search(self, *args, **kw):
        for dn in self:
            value = self[dn]
            attrs = {value[1][0]: value[1][1], value[0][0]: dn}
            yield [(dn, attrs)]

    def itervalues(self):
        return (Node(name=x[0][0], attrs=x[0][1]) for x in
                self._search(self.base_dn,
                             ldap.SCOPE_SUBTREE, attrlist=[''])
                if x[0][0] != self.base_dn)

#class ListBasedSet(collections.Set):
#     ''' Alternate set implementation favoring space over speed
#         and not requiring the set elements to be hashable. '''
#     def __init__(self, iterable):
#         self.elements = lst = []
#         for value in iterable:
#             if value not in lst:
#                 lst.append(value)
#     def __iter__(self):
#         return iter(self.elements)
#     def __contains__(self, value):
#         return value in self.elements
#     def __len__(self):
#         return len(self.elements)



class TestValuessView(mixins.Slapd, unittest.TestCase):
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

    def test_viewlen(self):
        def delete():
            del self.dir['cn=cn0,o=o']

        dn1 = 'cn=cn0,o=o'
        node1 = Node(name=dn1, attrs=self.ENTRIES[dn1])
        def addnode1():
            self.dir[dn1] = node1

        dn2 = 'cn=cn2,o=o'
        node2 = Node(name=dn2, attrs=self.ADDITIONAL[dn2])
        def addnode2():
            self.dir[dn2] = node2

        self.assertEqual(len(self.ENTRIES.values()), len(self.dir.values()))
        delete()
        self.assertTrue(len(self.ENTRIES.values()) > len(self.dir.values()))
        addnode1()
        addnode2()
        self.assertTrue(len(self.ENTRIES.values()) < len(self.dir.values()))

    def test_viewequal(self):
        dn = 'cn=cn0,o=o'
        node = Node(name=dn)
        dn1 = 'cn=cn1,o=o'
        node1 = Node(name=dn1)
        valuesList = [node, node1]

        values = self.dir.values()
        # XXX check the equality of view values!!!
        # it works even as no method exists?!?
        #self.assertTrue(values == values)
        #self.assertTrue(values == valuesList)
        #self.assertFalse(self.ENTRIES.values() != values)

        del self.dir['cn=cn0,o=o']
        values = self.dir.values()
        #self.assertTrue(self.ENTRIES.values() != values)

    def test_notequal(self):
        pass
        # XXX when test_viewequal is done

    def test_viewcontains(self):
        dn = 'cn=cn0,o=o'
        node = Node(name=dn)
        item = (dn, node)
        fail = 'cn=fail, o=o'
        failNode = Node(name=fail)
        values = self.dir.values()

        self.assertTrue(node in values)
        self.assertFalse(failNode in values)
