from setuptools import setup, find_packages
import sys, os

version = '0dev'
shortdesc = 'Access ldap via a dictionary tree.'
#longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

install_requires = [
    'setuptools'
]

if sys.version_info[0] is 2 and sys.version_info[1] < 7:
    install_requires.append('unittest2')

setup(name='dicttree.ldap',
      version=version,
      description=shortdesc,
      #long_description=longdesc,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        ],
      keywords='',
      author='Florian Friesdorf',
      author_email='flo@chaoflow.net',
      url='http://github.com/chaoflow/dicttree.ldap',
      license='BSD license',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['dicttree'],
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
      )
