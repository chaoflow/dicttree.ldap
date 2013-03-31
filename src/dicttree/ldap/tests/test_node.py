from unittest import TestCase

from dicttree.ldap._node import Node

class BadNode(Node):
    """Ignores name and returns an ever incrementing name
    """
    counter = 0

    @property
    def name(self):
        self.counter += 1
        return str(self.counter)
    @name.setter
    def name(self, x):
        pass


class TestBadNode(TestCase):
    def test_never_the_same_name(self):
        node = BadNode()
        self.assertEqual(node.name, '1')
        self.assertEqual(node.name, '2')
        self.assertNotEqual(node.name, node.name)


class TestNode(TestCase):
    def test_repr(self):
        node = Node(name='a')
        self.assertEqual('<ldap node dn="a">', repr(node))

    def test_same_is_equal_short_circuit(self):
        node = BadNode()
        self.assertEqual(node, node)

    def test_name_equality(self):
        node1 = Node(name='a')
        node2 = Node(name='a')
        other = Node(name='b')

        self.assertTrue(node1 == node2)
        self.assertFalse(node1 != node2)
        self.assertTrue(node1 != other)
        self.assertFalse(node1 == other)

        self.assertEqual(node1, node2)
        self.assertNotEqual(node1, other)

    def test_attrs_equality(self):
        node1 = Node(name='name', attrs=(('a', '1'), ('b', '2')))
        node2 = Node(name='name', attrs=(('a', '1'), ('b', '2')))
        more =  Node(name='name', attrs=(('a', '1'), ('b', '2'), ('c', '3')))
        less =  Node(name='name', attrs=(('a', '1'),))
        other = Node(name='name', attrs=(('a', '2'), ('b', '1')))
        order = Node(name='name', attrs=(('b', '2'), ('a', '1')))

        self.assertEqual(node1, node2)
        self.assertNotEqual(node1, more)
        self.assertNotEqual(node1, less)
        self.assertNotEqual(node1, other)
        # (currently) ldap attributes are not ordered (see dicttree.ldap.Node)
        self.assertEqual(node1, order)
        #self.assertNotEqual(node1, order)

    def test_attrs_order(self):
        attrlist = (('a', ['1']), ('b', ['2']))
        node = Node(attrs=attrlist)
        self.assertEquals(attrlist, tuple(node.attrs.items()))
