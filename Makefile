# loglevels for SLAPD_LOGLEVEL, comma-separated
# 1      (0x1 trace) trace function calls
# 2      (0x2 packets) debug packet handling
# 4      (0x4 args) heavy trace debugging (function args)
# 8      (0x8 conns) connection management
# 16     (0x10 BER) print out packets sent and received
# 32     (0x20 filter) search filter processing
# 64     (0x40 config) configuration file processing
# 128    (0x80 ACL) access control list processing
# 256    (0x100 stats) connections, LDAP operations, results (recommended)
# 512    (0x200 stats2) stats log entries sent
# 1024   (0x400 shell) print communication with shell backends
# 2048   (0x800 parse) entry parsing

export SLAPD_LOGLEVEL := stats
export KEEP_FAILED := 1

all: check

bootstrap: dev.nix requirements.txt setup.py
	nix-env -p nixprofile -i dev-env -f dev.nix
	./nixprofile/bin/virtualenv --distribute --clear .
	echo ../../../nixprofile/lib/python2.7/site-packages > lib/python2.7/site-packages/nixprofile.pth
	./bin/pip install -r requirements.txt --no-index -f ""
	./bin/easy_install -H "" ipython
	./bin/easy_install -H "" ipdb
	./bin/easy_install -H "" flake8
	./bin/easy_install -H "" pylint

bin/nosetests:
	./bin/easy_install -H "" nose

print-syspath:
	./bin/python -c 'import sys,pprint;pprint.pprint(sys.path)'


var:
	test -L var -a ! -e var && rm var || true
	ln -s $(shell mktemp --tmpdir -d dicttree.ldap-var-XXXXXXXXXX) var

var-clean:
	rm -fR var/*

check: var var-clean bin/nosetests
	./bin/nosetests -v -w . --processes=4 ${ARGS}

check-debug: var var-clean bin/nosetests
	DEBUG=1 ./bin/nosetests -v -w . --ipdb --ipdb-failures ${ARGS}

coverage: var var-clean bin/nosetests
	rm -f .coverage
	./bin/nosetests -v -w . --with-cov --cover-branches --cover-package=dicttree.ldap ${ARGS}


pyoc-clean:
	find . -name '*.py[oc]' -print0 |xargs -0 rm

update-ldap-schema:
	mkdir -p etc/openldap/schema
	cp nixprofile/etc/openldap/schema/* etc/openldap/schema/

.PHONY: all bootstrap check coverage print-syspath pyoc-clean test-nose var var-clean
