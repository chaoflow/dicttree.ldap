import itertools
import os
import shutil
import sys
import tempfile
import time
import traceback
import urllib

from ldap.ldapobject import LDAPObject
from subprocess import Popen, PIPE

from dicttree.ldap import Directory


class Slapd(object):
    def setUp(self):
        try:
            self._setUp()
        except Exception, e:
            # XXX: working around nose to get immediate exception
            # output, not collected after all tests are run
            sys.stderr.write("""
======================================================================
Error setting up testcase: %s
----------------------------------------------------------------------
%s
""" % (str(e), traceback.format_exc()))
            self.tearDown()
            raise e

    def _setUp(self):
        """start slapd

        ldap data dir is wiped and a fresh base dn added. In case of
        errors the SLAPD process is supposed to be killed.
        """
        self.basedir = '/'.join(['var', self.id()])
        os.mkdir(self.basedir)

        datadir = '/'.join([self.basedir, 'data'])
        os.mkdir(datadir)

        shutil.copytree('etc/openldap/schema', '/'.join([self.basedir, 'schema']))

        # start ldap server
        self.slapdbin = os.path.abspath("nixenv/libexec/slapd")
        self.slapdconf = os.path.abspath("etc/openldap/slapd.conf")
        self.uri = 'ldapi://' + \
            urllib.quote('/'.join([self.basedir, 'ldapi']), safe='')
        self.loglevel = os.environ.get('SLAPD_LOGLEVEL', '0')
        self.debug = bool(os.environ.get('DEBUG'))
        self.debugflags = tuple(itertools.chain.from_iterable(
                iter(('-d', x)) for x in self.loglevel.split(',')))
        self.slapd = Popen(
            (self.slapdbin,
             "-f", self.slapdconf,
             "-s", "0",
             "-h", "ldapi://ldapi") + self.debugflags,
            cwd=self.basedir,
            stdout=PIPE if not self.debug else None,
            stderr=PIPE if not self.debug else None)

        # wait for ldap to appear
        waited = 0
        while True:
            try:
                self.ldap = LDAPObject(self.uri)
                self.ldap.bind_s('cn=root,o=o', 'secret')
            except:
                if waited > 10:
                    self.tearDown()
                    raise
                time.sleep(0.1)
                waited = waited + 1
            else:
                break

        # add base dn and per testcase entries
        self.ldap.add_s('o=o', (('o', 'o'),
                                ('objectClass', 'organization'),))

        msgids = [self.ldap.add(dn, self.ENTRIES[dn])
                  for dn in getattr(self, 'ENTRIES', ())]
        for id in msgids:
            self.ldap.result(id)

        self.dir = Directory(uri=self.uri,
                             base_dn='o=o',
                             bind_dn='cn=root,o=o',
                             pw='secret')

    def tearDown(self):
        self.slapd.kill()
        self.slapd.wait()
        successful = sys.exc_info() == (None, None, None)
        if successful or not os.environ['KEEP_FAILED']:
            shutil.rmtree(self.basedir)

