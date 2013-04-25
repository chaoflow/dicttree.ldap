"""Using users entryUUID from ldap as distinguished name
"""
from __future__ import absolute_import

from dicttree.ldap._directory import Directory
from dicttree.ldap.aspects import entryUUID

Directory = entryUUID(Directory)
