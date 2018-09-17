#!/usr/bin/env python3

'''
exotransmit.io
==============
Deals with input and output of files, editing parameter files and moving
    output files to the required locations

Functionality:
- Set up initial ExoTransmit structure, based off number of available cores
- Set parameters within userInput.in
- Creates consistent file naming
- Loads spectral data for a planet
- Lists and fetches eos names and codes using eos_list.txt

Contents
--------
Modules
*******
eos : Deals with equation of state selection
filehandler : Deals with creating standardised file names, saving and Loading
    spectral data, singly or an entire grid.
parameters : Deals with setting the parameters for a run of Exo-Transmit

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

from .eos import get_eos, list_eos, enumerate_eos, list_path
from .filehandler import make_file_name, create_folders, load_spectral_data, get_params_from_file
from .parameters import set_parameters, get_parameters, _check_planet_units, _check_star_units

eos_list_path = list_path
