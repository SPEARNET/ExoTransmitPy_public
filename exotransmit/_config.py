#!/usr/bin/env python3

'''
exotransmit.config
==================

Config file for Exo-Transmit python handler.

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
import multiprocessing as mp
import errno
import shutil
import socket

# Makes the path to config.txt, which MUST be in the same directory as this file
PATH_TO_ORIGINAL_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'include/__config_original.txt')
if not os.path.exists(PATH_TO_ORIGINAL_CONFIG_FILE):
    raise FileNotFoundError('exotransmit/include/__config_original.txt could not be found. Please ensure it is in the correct place.')

config_fname = '_config-{}.txt'.format(socket.gethostname())

PATH_TO_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'include/{}'.format(config_fname))


def _read_config_data():
    '''
    Reads in path data from exotransmit config.txt file

    Returns
    -------
    EXOTRANSMIT_URL : str
        The url address to the original github where Exo-Transmit is
        downloadable from
    EXOTRANSMIT_ORIGINAL_PATH : str
        The path to downloaded copy of Exo-Transmit
    EXOTRANSMIT_CLUSTER_PATH : str
        Path to parent folder of the Exo-Transmit cluster used by this module
    EXOTRANSMIT_SPECTRA_PATH : str
        Path to folder where spectra will be saved by default
    SETUP_COMPLETED : bool
        Flag to show if the setup of Exo-Transmit has been completed.
    '''
    if os.path.exists(PATH_TO_CONFIG_FILE):
        path_to_config = PATH_TO_CONFIG_FILE
    else:
        path_to_config = PATH_TO_ORIGINAL_CONFIG_FILE

    with open(path_to_config, 'r') as f:
        config_file_lines = [line.strip() for line in f.readlines()]

    EXOTRANSMIT_URL = config_file_lines[5]

    EXOTRANSMIT_ORIGINAL_PATH = os.path.expanduser(config_file_lines[7])

    EXOTRANSMIT_CLUSTER_PATH = os.path.expanduser(config_file_lines[9])

    EXOTRANSMIT_SPECTRA_PATH = os.path.expanduser(config_file_lines[11])

    if config_file_lines[13] == 'False':
        SETUP_COMPLETED = False
    elif config_file_lines[13] == 'True':
        SETUP_COMPLETED = True
    else:
        raise Exception('ERROR: SETUP_COMPLETED value corrupted.')

    return EXOTRANSMIT_URL, EXOTRANSMIT_ORIGINAL_PATH, EXOTRANSMIT_CLUSTER_PATH, EXOTRANSMIT_SPECTRA_PATH, SETUP_COMPLETED


def _configure_exotransmit_cluster(reconfigure=False):
    '''
    Configures Exo-Transmit to run on multiple cores

    Parameters
    ----------
    reconfigure : bool, optional
        If True, will ask for confimation and reset the configuration, before
            configuring from fresh. Default False

    Returns
    -------
    EXOTRANSMIT_URL : str
        The url address to the original github where Exo-Transmit is
        downloadable from
    EXOTRANSMIT_ORIGINAL_PATH : str
        The path to downloaded copy of Exo-Transmit
    EXOTRANSMIT_CLUSTER_PATH : str
        Path to parent folder of the Exo-Transmit cluster used by this module
    EXOTRANSMIT_SPECTRA_PATH : str
        Path to folder where spectra will be saved by default
    EXOTRANSMIT_INSTANCE_PATHS : list of str
        List of paths to copies of Exo-Transmit that will be used here
    EXOTRANSMIT_INSTANCE_PATHS : list of str
        List of paths to the userInput.in file of each copy of Exo-Transmit

    Detailed description
    --------------------
    Reads _config.txt to see if full setup needs to be done. If so, will:
    - Request the path to a compiled copy of Exo-Transmit
    - Make n copies of Exo-Transmit in a folder called 'ExoTransmitCluster'
    - Create a folder called 'ExoTransmitSpectra' where generated spectra will
        be saved.


    '''
    if reconfigure:
        confirm = _reset_exotransmit()

        if not confirm:
            return

    EXOTRANSMIT_URL, EXOTRANSMIT_ORIGINAL_PATH, EXOTRANSMIT_CLUSTER_PATH, EXOTRANSMIT_SPECTRA_PATH, SETUP_COMPLETED = _read_config_data()

    if not SETUP_COMPLETED:

        # Create a user version of the blank config file which we can then edit
        shutil.copy(PATH_TO_ORIGINAL_CONFIG_FILE, PATH_TO_CONFIG_FILE)

        # Ask for path to existing original Exo-Transmit and then write this
        # to file
        while not os.path.exists(EXOTRANSMIT_ORIGINAL_PATH):
            EXOTRANSMIT_ORIGINAL_PATH = os.path.expanduser(input('Please give the path to the compiled copy of Exo-Transmit: '))
            print(EXOTRANSMIT_ORIGINAL_PATH)

        with open(PATH_TO_CONFIG_FILE, 'r') as f:
            config_file_lines = f.readlines()

        config_file_lines[7] = EXOTRANSMIT_ORIGINAL_PATH + '\n'

        with open(PATH_TO_CONFIG_FILE, 'w') as f:
            f.writelines(config_file_lines)

        # Now make the cluster and spectra folders!

        try:
            n_cores = mp.cpu_count()

            # Get the directory that the original exotransmit is in.
            EXOTRANSMIT_ORIGINAL_DIR = os.path.dirname(EXOTRANSMIT_ORIGINAL_PATH)

            #############################
            # EXOTRANSMIT CLUSTER SETUP #
            #############################

            if EXOTRANSMIT_CLUSTER_PATH == '':
                # No path is specified in the config.txt file - default to same directory Exo-Transmit is in
                # Update config.txt with this new path
                EXOTRANSMIT_CLUSTER_PATH = os.path.join(EXOTRANSMIT_ORIGINAL_DIR, 'ExoTransmitCluster/{}'.format(socket.gethostname()))

                with open(PATH_TO_CONFIG_FILE, 'r') as f:
                    config_file_lines = f.readlines()

                config_file_lines[9] = EXOTRANSMIT_CLUSTER_PATH + '\n'

                with open(PATH_TO_CONFIG_FILE, 'w') as f:
                    f.writelines(config_file_lines)

            if not os.path.exists(EXOTRANSMIT_CLUSTER_PATH):

                # Exo-Transmit cluster does not exist - make it!
                print('Creating Exo-Transmit cluster at {}'.format(EXOTRANSMIT_CLUSTER_PATH))

                # Create the ExoTransmitCluster directory
                try:
                    os.makedirs(EXOTRANSMIT_CLUSTER_PATH)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise

                # Create the copies of Exo-Transmit in the new cluster directory
                for i in range(n_cores):
                    try:
                        print('Creating Exo-Transmit copy {} of {}'.format(i+1, n_cores))

                        # Make the path name
                        exotransmit_copy_path = os.path.join(EXOTRANSMIT_CLUSTER_PATH, 'ExoTransmit{}'.format(i+1))

                        # Copy Exo-Transmit into this new directory
                        shutil.copytree(EXOTRANSMIT_ORIGINAL_PATH, exotransmit_copy_path)

                        # Change home directory path in the new userInput file.
                        with open(exotransmit_copy_path + '/userInput.in', 'r') as f:
                            userIn = f.readlines()
                        userIn[3] = exotransmit_copy_path + '\n'
                        with open(exotransmit_copy_path + '/userInput.in', 'w') as f:
                            f.writelines(userIn)

                    except FileExistsError as exception:
                        if exception.errno != errno.EEXIST:
                            raise

                    # TODO: should probably check to see if there is anything
                    # already in the Spectra folder of each copy and delete
                    # so as not to clog it all up!

            #####################################
            # EXOTRANSMIT SPECTRUM FOLDER SETUP #
            #####################################

            if EXOTRANSMIT_SPECTRA_PATH == '':
                # No path is specified in the config.txt file - default to same directory Exo-Transmit is in
                # Update config.txt with this new path
                EXOTRANSMIT_SPECTRA_PATH = os.path.join(EXOTRANSMIT_ORIGINAL_DIR, 'ExoTransmitSpectra')

                with open(PATH_TO_CONFIG_FILE, 'r') as f:
                    config_file_lines = f.readlines()

                config_file_lines[11] = EXOTRANSMIT_SPECTRA_PATH + '\n'

                with open(PATH_TO_CONFIG_FILE, 'w') as f:
                    f.writelines(config_file_lines)

            else:
                # Path is specified in config.txt
                EXOTRANSMIT_SPECTRA_PATH = os.path.join(EXOTRANSMIT_SPECTRA_PATH, 'ExoTransmitSpectra')

            # TODO: make the spectra directory.
            if not os.path.exists(EXOTRANSMIT_SPECTRA_PATH):
                print('Exo-Transmit spectra folder does not exist. Creating at path {}'.format(EXOTRANSMIT_SPECTRA_PATH))

                # Create the ExoTransmitSpectra directory
                try:
                    os.makedirs(EXOTRANSMIT_SPECTRA_PATH)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise

            # Update SETUP_COMPLETED to reflect completed setup
            with open(PATH_TO_CONFIG_FILE, 'r') as f:
                config_file_lines = f.readlines()

            config_file_lines[13] = 'True\n'

            with open(PATH_TO_CONFIG_FILE, 'w') as f:
                f.writelines(config_file_lines)
        except:
            raise

    # Find the paths to the copies of Exo-Transmit within the cluster
    # so we can call them later when we need to.
    EXOTRANSMIT_INSTANCE_PATHS = [os.path.join(EXOTRANSMIT_CLUSTER_PATH, instance) for instance in next(os.walk(EXOTRANSMIT_CLUSTER_PATH))[1]]

    # Find the paths to the userInput.in for each copy of Exo-Transmit
    EXOTRANSMIT_INPUT_PATHS = [ET + '/userInput.in' for ET in EXOTRANSMIT_INSTANCE_PATHS]

    return EXOTRANSMIT_URL, EXOTRANSMIT_ORIGINAL_PATH, EXOTRANSMIT_CLUSTER_PATH, EXOTRANSMIT_SPECTRA_PATH, EXOTRANSMIT_INSTANCE_PATHS, EXOTRANSMIT_INPUT_PATHS


def _reset_exotransmit():
    '''
    This will reset the

    '''
    with open(PATH_TO_CONFIG_FILE, 'r') as f:
        config_file_lines = f.readlines()
    with open(PATH_TO_CONFIG_FILE, 'r') as f:
        stripped_lines = [line.strip() for line in f.readlines()]

    original_cluster_location = os.path.expanduser(stripped_lines[9])
    original_spectra_location = os.path.expanduser(stripped_lines[11])

    # Confirm user definitely 100% wants to reconfigure - it will delete any data.
    confirm = ''
    while not confirm.lower() == 'y' and not confirm.lower() == 'n':
        confirm = input('WARNING: Reconfiguring Exo-Transmit will delete the Exo-Transmit copies in {} and any spectra saved in {}. Do you wish to proceed? y/[n] '.format(original_cluster_location, original_spectra_location))
        if confirm == '':
            confirm = 'n'

    if confirm.lower() == 'y':
        confirm = ''
        while not confirm.lower() == 'y' and not confirm.lower() == 'n':
            confirm = input('WARNING: Are you 100% sure? There is no way to retrieve your deleted spectra if you do this! y/[n] '.format(original_cluster_location, original_spectra_location))
            if confirm == '':
                confirm = 'n'

    if confirm == 'n':
        print('Reconfigure aborted')
        return False

    # Delete any existing folders
    if os.path.exists(original_cluster_location):
        print('Deleting existing cluster')
        shutil.rmtree(original_cluster_location)

    if os.path.exists(original_spectra_location):
        print('Deleting existing spectra')
        shutil.rmtree(original_spectra_location)

    # Reset the config.txt file
    config_file_lines[7] = '\n'
    config_file_lines[9] = '\n'
    config_file_lines[11] = '\n'
    config_file_lines[13] = 'False\n'
    with open(PATH_TO_CONFIG_FILE, 'w') as f:
        f.writelines(config_file_lines)

    return True
