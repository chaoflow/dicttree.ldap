# An environment to develop on dicttree.hydra
{ }:

with import <nixpkgs> {};

buildEnv {
  name = "dev-env";
  paths = [
    (openldap.override { cyrus_sasl = null; openssl = null; })
    python27
    python27Packages.coverage
    python27Packages.flake8
    python27Packages.ipdb
    python27Packages.ipdbplugin
    python27Packages.ipython
    python27Packages.ldap
    python27Packages.nose
    python27Packages.pylint
    python27Packages.recursivePthLoader
    python27Packages.sqlite3
    python27Packages.virtualenv
    python27Packages.zope_interface
  ] ++ lib.attrValues python27.modules;
}