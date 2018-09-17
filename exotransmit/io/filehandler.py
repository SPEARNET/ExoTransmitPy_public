#!/usr/bin/env python3

'''
exotransmit.io.filehandler
==========================

Module for handling files within ExoTransmit
- Standardised file naming
- Loading spectral data for a given planet (checks if this exists)

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

from exotransmit import EXOTRANSMIT_SPECTRA_PATH
from exotransmit.io import eos
import os
import numpy as np
import astropy.constants as c
import astropy.units as u
import errno


def make_file_name(planet_info):
    '''
    Makes a standardised file name for a planet

    Parameters
    ----------
    planet_info : arr or list
        Information of the planet to make the file name for. Must be of the
        form [eos code, T, g, Rp, Rs, P, r]

    Returns
    -------
    file_name : str
        Standardised file name

    See Also
    --------
    make_file_name : Generates a standardised file name with added letter code
                     identifying the nature of the spectrum.

    Notes
    -----
    The file naming convention used by this function is
        A_B_C_D_E_F_G.dat
        A - Equation of state name (from eos_list.txt)
        B - Equilibrium temperature in K
        C - surface gravity in m/s2
        D - Planet radius in Jupiter radii
        E - Stellar radius in Solar radii
        F - Cloud top pressure in Pa
        G - Rayleigh scattering factor
    '''
    return '{0}-{1:.1f}-{2:.2f}-{3:.2f}-{4:.2f}-{5:.2f}-{6:.2f}.dat'.format(
        eos.get_eos(planet_info[0]), planet_info[1], planet_info[2],
        planet_info[3], planet_info[4], planet_info[5], planet_info[6])


def create_folders(full_path):
    '''
    Given a full path to a file, creates the required folders

    Parameters
    ----------
    full_path : str
        Full path to a file. This must include the file name, as the function
        works by removing this from the string an creating the necessary
        folders from that.
    '''
    if not os.path.exists(full_path):
        try:
            os.makedirs(os.path.dirname(full_path))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


def load_spectral_data(path_or_planet_info):
    '''
    Loads spectral data if it exists.

    Parameters
    ----------
    path_or_planet_info : str or list
        Either a full path to a spectrum, or list of planet parameters in the
        form [eos code, T, g, Rp, Rs, P, r]. If planet parameters are provided,
        all possible standard locations will be searched for spectral data.

    Returns
    -------
    spectral_data : ndarray
        The spectrum, which is an array of wavelength and transit depth.
    '''
    if type(path_or_planet_info) is list or np.ndarray and len(path_or_planet_info) == 7:
        planet_info = path_or_planet_info
        # File name without letter code
        base_name = make_file_name(planet_info)

        eos_name = eos.get_eos(planet_info[0])
        paths_checked = []

        path = EXOTRANSMIT_SPECTRA_PATH + '/{0}/{1}/{2}'.format(eos_name, int(planet_info[1]), base_name)

        paths_checked.append(path)

        if os.path.exists(path):
            data = np.loadtxt(path, skiprows=3)
            return data

        raise Exception('Planet data does not exist!\nHave checked at {}'.format(paths_checked))

    elif type(path_or_planet_info) is str or (type(path_or_planet_info) is list or np.ndarray and len(path_or_planet_info) == 1):
        path = path_or_planet_info
        if os.path.exists(path):
            data = np.loadtxt(path, skiprows=3)
            return data
        else:
            raise Exception('Path {} does not exist'.format(path))

    else:
        raise Exception('Unable to determine the nature of path_or_planet_info. I was given this: {}'.format(path_or_planet_info))


def get_params_from_file(path_to_spectrum_file, units=False):
    '''
    Returns the parameters used to generate a spectrum

    Parameters
    ----------
    path_to_spectrum_file : str
        Full path to spectrum to obtain parameters from.
    units : bool, optional
        If True, parameters are returned with relevant astropy units attached
        to them. Default is False

    Returns
    -------
    spectrum_parameters : list
        Parameters used to generate the spectrum. If units is True, astropy
        units are attached to the relevant parameters. Listed in order
            EOS (code)
            Temperature (K)
            gravity (m/s2)
            planet radius (rjup)
            stellar radius (rsun)
            cloud top pressure (Pa)
            rayleigh factor (arbitrary units)

    '''

    # Find numerical parameters from file
    with open(path_to_spectrum_file, 'r') as f:
        txt_line = f.readline().strip()

    params_list = txt_line.split(', ')
    params_list = [i.split(':') for i in params_list]

    params = np.asarray(params_list, dtype=object)

    # Note that this catch is for older spectrum files where the EOS was Not
    # Included in the header. As of 13/4/18, the EOS is included in the header.
    if len(params) == 6:
        params = params[:, 1].astype('float')
        # Convert to jupiter and solar radii
        params[2] = params[2] / c.R_jup.value
        params[3] = params[3] / c.R_sun.value

        # Find EOS and associated code from the file name
        fname = os.path.basename(path_to_spectrum_file)
        eos_string = fname.split('-')[0]
        eos_code = eos.enumerate_eos(eos_string)

        if units:
            # add the units

            T = params[0] * u.K
            g = params[1] * u.m * u.s**-2
            rp = params[2] * u.R_jup
            rs = params[3] * u.R_sun
            p = params[4] * u.Pa
            r = params[5]

            params_units = np.array([eos_code, T, g, rp, rs, p, r], dtype=object)
            return params_units

        else:
            params = np.hstack((eos_code, params))
            return params

    # Params has been read in as str. Deal with the multiple dtypes here
    str_params = params[:, 1]
    float_params = str_params[1:].astype(float).astype(object)
    params = np.hstack((str_params[0], float_params))

    # Convert to jupiter and solar radii
    params[3] = params[3] / c.R_jup.value
    params[4] = params[4] / c.R_sun.value

    # Find EOS and associated code from the file name
    fname = os.path.basename(path_to_spectrum_file)
    eos_string = params[0]
    eos_code = eos.enumerate_eos(eos_string)

    if units:
        # add the units

        T = params[1] * u.K
        g = params[2] * u.m * u.s**-2
        rp = params[3] * u.R_jup
        rs = params[4] * u.R_sun
        p = params[5] * u.Pa
        r = params[6]

        params_units = np.array([eos_code, T, g, rp, rs, p, r], dtype=object)
        return params_units

    else:
        params = np.hstack((eos_code, params[1:]))
        return params
