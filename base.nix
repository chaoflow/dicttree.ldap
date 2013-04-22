{ python, pythonPackages, pythonDocs ? null }:

with import <nixpkgs> {};

{
  paths = [ python ] ++
          (lib.optionals (pythonDocs != null) [ pythonDocs ]) ++
          (with pythonPackages;
           [
             argparse
             coverage
             epc
             flake8
             ipdb
             ipdbplugin
             ipython
             jedi
             nose
             pylint
             recursivePthLoader
             sqlite3
             unittest2
             virtualenv
           ]) ++ lib.attrValues python.modules;
}
