#!/usr/bin/env python3

'''
exotransmit.core
================

Top level functions for running Exo-Transmit

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

from exotransmit import io
from exotransmit import EXOTRANSMIT_SPECTRA_PATH, EXOTRANSMIT_INSTANCE_PATHS
import os
import errno
import shutil
import subprocess
import numpy as np
import multiprocessing as mp
from copy import deepcopy


def run(planet_parameters, output_path=None, clobber=False, ncores=mp.cpu_count(),
        return_paths=False):
    """
    Runs ExoTransmit on a planet or list of planets to create spectrum files.

    Parameters
    ----------
    planet_parameters : list
        List of the parameters to run. May be specifying an individual planet,
        with format [eos, T, g, Rp, Rs, P, r], or multiple planets, with
        format [[eos1, T1, g1, Rp1, Rs1, P1, r1],
                [eos2, T2, g2, Rp2, Rs2, P2, r2]]
    output_path : str or list of str, optional
        Output path to save spectrum to. EXOTRANSMIT_SPECTRA_PATH will be
        prepended to the supplied path.
        If not supplied, the path will be automatically generated.
        If supplied, and more than one planet is to be simulated, length of
        the list of planets and the list of output paths must be equal.
    clobber : bool, optional
        If true, existing spectra with the same path will be overwritten.
        Default is False
    ncores : int, optional
        The number of cores of the machine to make available to ExoTransmit. If
        more than one planet is supplied and more than one core is available,
        the function will split planets evenly between the available cores to
        reduce the overall runtime of the function. Default is the total number
        of cores on the machine.
    return_paths : bool, optional
        If True, will return the paths within ExoTransmitSpectra where the
        output spectra have been saved. Default False

    Returns
    ---------
    output_paths : list, optional
        Paths to where the outputs have been saved within ExoTransmitSpectra
        if return_paths is True.
    """

    # SUBPROCESS ##############################################################
    def exotransmit_subprocess(parameter_list, output_list, n):
        '''
        Subprocess to chew through a list of planets using one instance of
            ExoTransmit (denoted by n)
        planet_list and output_list are np.ndarrays

        '''
        # set so that the user feedback on cores is presented in a
        # readable way
        core_n = n + 1

        if parameter_list.ndim == 1:
            # a single set of parameters has been passed. Reformat it so we can
            # pass it to the cores!
            parameter_list = np.array([parameter_list])
            output_list = np.array([output_list])

        # Begin the simulations!
        print('Core {} starting {} jobs'.format(core_n, len(parameter_list)))

        for i, parameters in enumerate(parameter_list):
            # Check to see if spectrum has already been generated
            if os.path.exists(os.path.join(EXOTRANSMIT_SPECTRA_PATH, output_list[i])) and not clobber:
                print(
                    'Data for this planet already exists!\n'
                    'Please use clobber=True to overwrite.\n{}'.format(parameters))
            else:
                _exotransmit_direct_run(parameters, output_list[i], n)

            print('Core {}: {}/{} jobs completed'.format(core_n,
                                                         i + 1, len(parameter_list)))

    ###########################################################################
    # MAIN FUNCTION ###########################################################

    if ncores > mp.cpu_count():
        raise Exception('ncores={} was specified, but this machine only has {} cores!'.format(
            ncores, mp.cpu_count()))

    # Cast planets to numpy array if necessary - by checking the number of
    # dimensions, we can see if we have been asked to do more than one planet 
    planet_parameters = np.asarray(planet_parameters, dtype=object)

    # Check that the Eos codes are all ints, and change them if needed.
    if planet_parameters.ndim == 1:
        if planet_parameters[0] % 1 == 0:
            if not type(planet_parameters[0]) is int:
                planet_parameters[0] = int(planet_parameters[0])
        else:
            raise TypeError('Unable to safely convert input EoS {} into int value'.format(planet_parameters[0]))
    else:
        for params in planet_parameters:
            if params[0] % 1 == 0:
                if not type(params[0]) is int:
                    params[0] = int(params[0])
            else:
                raise TypeError('Unable to safely convert input EoS {} into int value'.format(params[0]))



    if output_path is None:
        # Generate file names
        if planet_parameters.ndim == 1:
            output_path = ['{}/{}/{}'.format(io.get_eos(planet_parameters[0]), int(
                planet_parameters[1]), io.make_file_name(planet_parameters))]
        else:
            output_path = []
            for param_set in planet_parameters:
                output_path.append('{}/{}/{}'.format(io.get_eos(param_set[0]), int(
                    param_set[1]), io.make_file_name(param_set)))



    output_path = np.asarray(output_path, dtype=object)
    # Make the full final output paths of the spectra so we can return this.
    full_output_path = deepcopy(output_path)
    for i, path in enumerate(full_output_path):
        full_output_path[i] = os.path.join(EXOTRANSMIT_SPECTRA_PATH, path)

    if not len(planet_parameters) == len(output_path):
        if not planet_parameters.ndim == len(output_path):
            raise Exception(
                'ERROR: Number of planets and outputs do not match')

    # FOR SINGLE PLANET #######################################################

    if planet_parameters.ndim == 1:
        if os.path.exists(os.path.join(EXOTRANSMIT_SPECTRA_PATH, output_path[0])) and not clobber:
            print(
                'Data for this planet already exists!\n'
                'Please use clobber=True to overwrite.\n{}'.format(planet_parameters))
        else:
            print('Simulating planet...')
            _exotransmit_direct_run(planet_parameters, output_path.item())

    # FOR MULTIPLE PLANETS ####################################################

    # N PLANETS < N CORES #####################################################
    else:
        if len(planet_parameters) < ncores:
            # Not all cores are needed, so we can do this separately.
            jobs = []
            for n in range(len(planet_parameters)):
                process = mp.Process(target=exotransmit_subprocess,
                                     args=(planet_parameters[n], output_path[n], n))
                jobs.append(process)
                process.start()

    # N PLANETS > N CORES #####################################################
        else:
            # Split arrays for each core
            planet_parameters_split = np.array_split(planet_parameters, ncores)
            output_path = np.array_split(output_path, ncores)

            jobs = []
            for n in range(ncores):
                process = mp.Process(target=exotransmit_subprocess,
                                     args=(planet_parameters_split[n], output_path[n], n))
                jobs.append(process)
                process.start()

        for process in jobs:
            process.join()

    if return_paths:
        return full_output_path


def _exotransmit_direct_run(planet_parameters, output_path, n=0):
    '''
    Subroutine running ExoTransmit on a single planet

    This funtion should not be called directly. For general use, please use
    >>> exotransmit.run(planets)
    which calls this subroutine

    Parameters
    ----------
    eos_code : int
        Specify using code from exotransmit.io.eos_list()
    T : int
        Equilibrium temperature. Must be a multiple of 100K between 300K and
        1500K
    surface_gravity : float
        Strength of gravity in m/s2 at surface (or P = 1bar)
    planet_radius : float
        Radius of planet. May be specified in m or in Jupiter radii - the init
        will detect which. Will be converted to and stored in jupiter radii
    stellar_radius : float
        Radius of the host star. May be specified in m or in solar radii - the
        init will detect which. Will be converted to and stored in solar radii
    cloud_top_pressure : float
        Pressure at cloud top in Pa
    rayleigh_factor : float
        Dimensionless rayleigh scattering factor. Earth equivalent is
        normalised to 1.
    output_path : str
        The path to save the spectrum to. This is saved within
        /ExoTransmitSpectra, so you can't specify explicitly a full path
        to save your spectrum to. This may change in later releases.
    n : int, optional
        Specifies the instance of ExoTransmit being used
    '''

    # Format output path appropriately
    if not output_path[-4:] == '.dat':
        output_path += '.dat'
    if not output_path[0] == '/':
        output_path = '/' + output_path

    output_file_name = os.path.basename(output_path)

    # Set parameters for the run
    io.set_parameters(planet_parameters[0], planet_parameters[1],
                      planet_parameters[2], planet_parameters[3],
                      planet_parameters[4], planet_parameters[5],
                      planet_parameters[6], output_file_name, n)

    # Run ExoTransmit - need to switch into appropriate directory and back
    # again
    current_dir = os.getcwd()

    os.chdir(EXOTRANSMIT_INSTANCE_PATHS[n])
    subprocess.check_output(['./Exo_Transmit'])
    os.chdir(current_dir)

    # ExoTransmit saves output spectra files within a folder in each
    # instance of ExoTransmit. To save to the specified output path, the
    # files must be moved manually, done here.

    desired_output_path = EXOTRANSMIT_SPECTRA_PATH + output_path
    default_output_path = EXOTRANSMIT_INSTANCE_PATHS[n] + \
        '/Spectra/' + output_file_name

    # Create folders to save output to
    if not os.path.exists(os.path.dirname(desired_output_path)):
        try:
            os.makedirs(os.path.dirname(desired_output_path))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    # Move the output file
    shutil.move(default_output_path, desired_output_path)

    # Prepend planet parameters to output file
    parameters_list = io.get_parameters(n)
    details_to_prepend = 'EoS:{}, T:{}, g:{}, r_p:{}, r_s:{}, P:{}, r:{}'.format(
        os.path.basename(parameters_list[0])[
            :-4], parameters_list[1], parameters_list[3],
        parameters_list[4], parameters_list[5], parameters_list[6],
        parameters_list[7])
    with open(desired_output_path, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(details_to_prepend.rstrip('\r\n') + '\n' + content)
