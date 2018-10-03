#!/usr/bin/env python3

'''
exotransmit
===========
Python 3 wrapper for Exo-Transmit, a program written by Kempton et al, available from
    https://github.com/elizakempton/Exo_Transmit.

Contents
--------
Modules
*******
config : configuration functions which calculate relevant paths to instances
    of Exo-Transmit

funcs : key functions involving running of Exo-Transmit

Sub-packages
************
io : Deals with input and output of files, editing parameter files and moving
    output files to the required locations
comparison : Used to compare different spectra
plotting : used for visualising spectra.


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
from . import _config

# Need to set up all the path information
EXOTRANSMIT_URL, EXOTRANSMIT_ORIGINAL_PATH, EXOTRANSMIT_CLUSTER_PATH, EXOTRANSMIT_SPECTRA_PATH, EXOTRANSMIT_INSTANCE_PATHS, EXOTRANSMIT_INPUT_PATHS = _config._configure_exotransmit_cluster()

from . import io
from .io import list_eos
from .core import run

# Metadata
__version__ = '1.1.0'
__author__ = 'Joshua Hayes'
__status__ = 'Development'
__contact__ = 'joshua.hayes@postgrad.manchester.ac.uk'
__copyright__ = 'Copyright 2018, Joshua Hayes'
