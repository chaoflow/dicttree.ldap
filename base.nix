{ python, pythonPackages, pythonDocs ? null }:

with import <nixpkgs> {};

{
  paths = [ python ] ++
          (lib.optionals (pythonDocs != null) [ pythonDocs ]) ++
          (with pythonPackages;
           [
             coverage
             elpy
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
