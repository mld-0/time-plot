#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1

import re
from distutils.core import setup
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('timeplot/__main__.py').read(),
    re.M
    ).group(1)

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

install_depend = [
    'dtscan',
    'dateparser',
    'matplotlib',
    'pandas',
    'tzlocal',
    'pytz',
    'taskblock-reader',
    'dtscan',
]

test_depend = [ 
    'pytest',
    'tox',
]

setup(
    name="timeplot",
    version=version,
    author="Matthew L Davis",
    author_email="mld.0@protonmail.com",
    description="Plotting <various> involving passage of time per day/week",
    long_description=long_descr,
    packages = ['timeplot', 'tests'],
    install_requires=install_depend,
    tests_require=test_depend,
    entry_points={
        'console_scripts': [ 
        'timeplot=timeplot.__main__:timeplotmain',
        ],
    }
)



