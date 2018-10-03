'''
Setup file for Exo-Transmit Python 3 wrapper

author: Josh Hayes
Contact: joshjchayes@gmail.com
Initial creation date: 11/05/2018

---------------------------------------------------------------------
ExoTransmitPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ExoTransmitPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ExoTransmitPy.  If not, see <http://www.gnu.org/licenses/>.
'''

from distutils.core import setup
from setuptools import find_packages
import os

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Install the Python libraries to machine
setup(
    name='exotransmit',
    version='1.1.0',
    packages=find_packages(),
    author='Joshua Hayes',
    author_email='joshua.hayes@postgrad.manchester.ac.uk',
    description='Python 3 wrapper for Exo-Transmit (Kempton 2017). Must have Exo-Transmit installed and compiled to known location for this wrapper to work.',
    long_description=read('README.rst'),
    package_data={'exotransmit': ['include/*']},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Science/Research',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
