# An environment to develop on dicttree.hydra
{ }:

with import <nixpkgs> {};

buildEnv {
  name = "dicttree-ldap-dev-env";
  paths = [
    openldap
    python27
    python27Packages.ipdb
    python27Packages.ipython
    python27Packages.nose
    python27Packages.coverage
    python27Packages.ldap
    python27Packages.recursivePthLoader
    python27Packages.sqlite3
    python27Packages.virtualenv
    python27Packages.zope_interface
  ] ++ lib.attrValues python27.modules;
}