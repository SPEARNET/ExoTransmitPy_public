#!/usr/bin/env python3

'''
exotransmit.io.parameters
================================

Module for setting parameters for running ExoTransmit in userInput.in

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

from exotransmit import EXOTRANSMIT_INPUT_PATHS
from exotransmit.io import get_eos
import re
import astropy.constants as c


def set_parameters(eos_code, T, g, Rp, Rs, P, r, output_name, n=0):
    '''
    Sets information in userInput.in appropriately for a given planetary system

    Parameters
    ----------
    planet : Planet
        Planet object to be simulated by ExoTransmit
    output_name : str
        Name of the file to save the output spectra to. Note that this is just
        the file name and not the path to save it to
    n : int
        The number of the core to run this simulation on

    '''
    Rp = _check_planet_units(Rp)
    Rs = _check_star_units(Rs)

    # Read in userInput
    with open(EXOTRANSMIT_INPUT_PATHS[n], 'r') as file:
        userIn = file.readlines()

    # Change relevant lines
    # Set output name
    if not output_name[-4:] == '.dat':
        output_name += '.dat'

    userIn[9] = '/Spectra/' + output_name + '\n'

    # Set TP file
    userIn[5] = '/T_P/t_p_{}K.dat\n'.format(int(T))

    # Set EOS file
    userIn[7] = '/EOS/' + get_eos(eos_code) + '.dat\n'

    # Set gravity
    userIn[11] = str(g) + '\n'

    # Set planet radius (in m)
    userIn[13] = str(round(Rp, 1)) + '\n'

    # Set star radius (in m)
    userIn[15] = str(round(Rs, 1)) + '\n'

    # Set cloud top pressure
    userIn[17] = str(P) + '\n'

    # Set rayleigh scattering factor
    userIn[19] = str(r) + '\n'

    with open(EXOTRANSMIT_INPUT_PATHS[n], 'w') as file:
        file.writelines(userIn)
    return 0


def get_parameters(n):
    '''
    Finds current planet parameters being used by ExoTransmit(n)

    Parameters
    ----------
    n : int
        The ExoTransmit instance of interest. This is interchangable with the
        number of the core the simulation is being run on.

    Returns
    ----------
    parameters : list
        List of current parameters as listed in userInput.in. List is in order
        [Temperature, Equation of state, output_name, gravity, planet radius,
        stellar radius, Cloud top pressure, rayleigh factor]
    '''
    with open(EXOTRANSMIT_INPUT_PATHS[n], 'r') as file:
        userIn = file.readlines()

    TP = userIn[5].rstrip('\r\n')
    TP = re.findall(r'\d+', TP)[0]
    EOS = userIn[7].rstrip('\r\n')
    output_name = userIn[9].rstrip('\r\n')
    gravity = userIn[11].rstrip('\r\n')
    R_p = userIn[13].rstrip('\r\n')
    R_s = userIn[15].rstrip('\r\n')
    P = userIn[17].rstrip('\r\n')
    r = userIn[19].rstrip('\r\n')

    parameters = [EOS, TP, output_name, gravity, R_p, R_s, P, r]

    return parameters


def _check_planet_units(Rp):
    '''
    Checks to see if the given planet radius is in m or R_jup. If R_jup,
    converts to m before setting the parameters in userInput.in

    Parameters
    ----------
    Rp : float
        Input planet radius as given by user

    Returns
    -------
    Rp_m : float
        Planet radius in m

    Notes
    -----
    This basically works by assuming that any number under 10 is in Jupiter
    radii and anything >10^6  and < 10^9 is in m. Anything inbetween is assumed
    to be a typo by the user and throws an exception
    '''
    if Rp < 10:
        # Jupiter Radii
        return Rp * c.R_jup.value
    elif 1e6 < Rp < 1e9:
        return Rp
    else:
        raise ValueError('Unable to detect planet radius units')


def _check_star_units(Rs):
    '''
    Checks to see if the given star radius is in m or R_sun. If R_sun,
    converts to m before setting the parameters in userInput.in

    Parameters
    ----------
    Rs : float
        Input star radius as given by user

    Returns
    -------
    Rs_m : float
        Star radius in m

    Notes
    -----
    This basically works by assuming that any number under 100 is in Solar
    radii and anything > 10^9  and < 10^12 is in m. Anything inbetween is assumed
    to be a typo by the user and throws an exception
    '''
    if Rs < 100:
        # Jupiter Radii
        return Rs * c.R_sun.value
    elif 1e11 < Rs < 1e12:
        return Rs
    else:
        raise ValueError('Unable to detect star radius units')
