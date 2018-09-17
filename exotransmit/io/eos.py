#!/usr/bin/env python3

'''
exotransmit.io.eos
==================

Module for equation of state selection within Exo-Transmit.

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

import os

list_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'include/eos_list.txt')


def get_eos(n):
    '''
    Finds the name of an equation of state file given by a numerical code.

    Parameters
    ----------
    n : int
        Equation of state numerical code. To see full list of codes, run
        >>> exotransmit.io.list_eos()

    Returns
    -------
    eos : str
        Name of the equation of state file.
    '''

    if not n % 1 == 0:
        raise ValueError('Code {} cannot be unambiguously converted into an integer index'.format(n))

    n = int(n)

    with open(list_path, 'r') as f:
        eos_list = [line.rstrip('\n') for line in f]

    return eos_list[n]


def list_eos():
    '''
    Prints available EOS with code to call them
    '''
    with open(list_path, 'r') as f:
        eos_list = [line.rstrip('\n') for line in f]

    print('Available Equations of State:')
    for i, eos in enumerate(eos_list):
        print('{}: {}'.format(i, eos))


def enumerate_eos(eos_name):
    '''
    Finds the code needed to reference an equation of state given by name

    Parameters
    ----------
    eos_name : str
        File name of the EOS the code is needed for.

    Returns
    -------
    code : int
        Integer code needed to reference the equation of state
    '''

    with open(list_path, 'r') as f:
        eos_list = [line.rstrip('\n') for line in f]

    try:
        return eos_list.index(eos_name)
    except ValueError:
        raise ValueError('Unrecognised EOS filename {}'.format(eos_name))
