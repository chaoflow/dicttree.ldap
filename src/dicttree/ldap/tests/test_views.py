import unittest

from dicttree.ldap._views import KeysView
from dicttree.ldap._views import ItemsView
from dicttree.ldap._views import ValuesView


class TestCase(unittest.TestCase):
    def setUp(self):
        self.dir = MockDirectory(a=1, b=2)
        self.dirEqual = MockDirectory(a=1, b=2)
        self.dirSimilar = MockDirectory(b=2, c=3)
        self.dirDifferent = MockDirectory(c=3, d=4, e=5)

class MockDirectory(dict):
    pass

class TestKeysView(TestCase):

    def setUp(self):
        super(TestKeysView, self).setUp()
        self.keys = KeysView(directory=self.dir)
        self.keysEqual = KeysView(directory=self.dirEqual)
        self.keysSimilar = KeysView(directory=self.dirSimilar)
        self.keysDifferent = KeysView(directory=self.dirDifferent)


    def test_equal(self):
        self.assertTrue(self.keys ==  self.keys)
        self.assertFalse(self.keys == self.keysSimilar)
        self.assertFalse(self.keys == self.keysDifferent)

    def test_notequal(self):
        self.assertFalse(self.keys != self.keysEqual)
        self.assertTrue(self.keys != self.keysSimilar)
        self.assertTrue(self.keys != self.keysDifferent)

    def test_len(self):
        self.assertEqual(len(self.keys), len(self.keysEqual))
        self.assertEqual(len(self.keys), len(self.keysSimilar))
        self.assertFalse(len(self.keys) == len(self.keysDifferent))

    def test_contains(self):
        self.assertTrue('a' in self.keys)
        self.assertFalse('a' in self.keysSimilar)

    def test_and(self):
        self.assertEqual(set(['a', 'b']), self.keys & self.keysEqual)
        self.assertEqual(set(['b']), self.keys & self.keysSimilar)
        self.assertEqual(set(), self.keys & self.keysDifferent)

    def test_or(self):
        self.assertEqual(set(['a', 'b']), self.keys | self.keysEqual)
        self.assertEqual(set(['a', 'b', 'c']), self.keys | self.keysSimilar)
        self.assertEqual(set(['a', 'b', 'c', 'd', 'e']),
                         self.keys | self.keysDifferent)

    def test_xor(self):
        self.assertEqual(set(), self.keys ^ self.keysEqual)
        self.assertEqual(set(['a', 'c']), self.keys ^ self.keysSimilar)
        self.assertEqual(set(['a', 'b', 'c', 'd', 'e']),
                         self.keys ^ self.keysDifferent)

    def test_sub(self):
        self.assertEqual(set(), self.keys - self.keysEqual)
        self.assertEqual(set(['a']), self.keys - self.keysSimilar)
        self.assertEqual(set(['a', 'b']),
                         self.keys - self.keysDifferent)

    def test_isdisjoint(self):
        self.assertFalse(self.keys.isdisjoint(self.keysEqual))
        self.assertFalse(self.keys.isdisjoint(self.keysSimilar))
        self.assertTrue(self.keys.isdisjoint(self.keysDifferent))


class TestItemsView(TestCase):

    def setUp(self):
        super(TestItemsView, self).setUp()
        self.items = ItemsView(directory=self.dir)
        self.itemsEqual = ItemsView(directory=self.dirEqual)
        self.itemsSimilar = ItemsView(directory=self.dirSimilar)
        self.itemsDifferent = ItemsView(directory=self.dirDifferent)


    def test_equal(self):
        self.assertTrue(self.items == self.items)
        self.assertFalse(self.items == self.itemsSimilar)
        self.assertFalse(self.items == self.itemsDifferent)

    def test_notequal(self):
        self.assertFalse(self.items != self.itemsEqual)
        self.assertTrue(self.items != self.itemsSimilar)
        self.assertTrue(self.items != self.itemsDifferent)

    def test_len(self):
        self.assertEqual(len(self.items), len(self.itemsEqual))
        self.assertEqual(len(self.items), len(self.itemsSimilar))
        self.assertFalse(len(self.items) == len(self.itemsDifferent))

    def test_contains(self):
        self.assertTrue(('a',1) in self.items)
        self.assertFalse(('a',1) in self.itemsSimilar)

    def test_and(self):
        self.assertEqual(set([('a', 1), ('b', 2)]),
                         self.items & self.itemsEqual)
        self.assertEqual(set([('b', 2)]), self.items & self.itemsSimilar)
        self.assertEqual(set(), self.items & self.itemsDifferent)

    def test_or(self):
        self.assertEqual(set([('a', 1), ('b', 2)]),
                         self.items | self.itemsEqual)
        self.assertEqual(set([('a', 1), ('b', 2), ('c', 3)]),
                         self.items | self.itemsSimilar)
        self.assertEqual(set([('a',1), ('b',2), ('c',3), ('d',4), ('e',5)]),
                         self.items | self.itemsDifferent)

    def test_xor(self):
        self.assertEqual(set(), self.items ^ self.itemsEqual)
        self.assertEqual(set([('a', 1), ('c', 3)]),
                         self.items ^ self.itemsSimilar)
        self.assertEqual(set([('a',1), ('b',2), ('c',3), ('d',4), ('e',5)]),
                         self.items ^ self.itemsDifferent)

    def test_sub(self):
        self.assertEqual(set(), self.items - self.itemsEqual)
        self.assertEqual(set([('a', 1)]), self.items - self.itemsSimilar)
        self.assertEqual(set([('a', 1), ('b', 2)]),
                         self.items - self.itemsDifferent)

    def test_isdisjoint(self):
        self.assertFalse(self.items.isdisjoint(self.itemsEqual))
        self.assertFalse(self.items.isdisjoint(self.itemsSimilar))
        self.assertTrue(self.items.isdisjoint(self.itemsDifferent))

class TestValuesView(TestCase):
    def setUp(self):
        super(TestValuesView, self).setUp()
        self.values = ValuesView(directory=self.dir)
        self.valuesEqual = ValuesView(directory=self.dirEqual)
        self.valuesSimilar = ValuesView(directory=self.dirSimilar)
        self.valuesDifferent = ValuesView(directory=self.dirDifferent)


    def test_equal(self):
        self.assertTrue(self.values == self.values)
        self.assertFalse(self.values == self.valuesSimilar)
        self.assertFalse(self.values == self.valuesDifferent)

    def test_notequal(self):
        self.assertFalse(self.values != self.valuesEqual)
        self.assertTrue(self.values != self.valuesSimilar)
        self.assertTrue(self.values != self.valuesDifferent)

    def test_len(self):
        self.assertEqual(len(self.values), len(self.valuesEqual))
        self.assertEqual(len(self.values), len(self.valuesSimilar))
        self.assertFalse(len(self.values) == len(self.valuesDifferent))

    def test_contains(self):
        self.assertTrue((1) in self.values)
        self.assertFalse((1) in self.valuesSimilar)

        #XXX add tests for list methods
