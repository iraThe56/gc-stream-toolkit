"""
NEMO File Reader Module

Converts NEMO simulation files to Gala-compatible format for stellar stream analysis.
"""

import os
import subprocess
import numpy as np
import astropy.units as u
import gala.dynamics as gala_dynamics


class NemoData:
    """
    Container for NEMO particle simulation data.

    Provides clean access to particle positions, velocities, and masses
    in both raw format and Gala PhaseSpacePosition format.
    """

    def __init__(self, positions, velocities, masses, time, particle_count):
        self.positions = positions
        self.velocities = velocities
        self.masses = masses
        self.time = time
        self.particle_count = particle_count

        # Create Gala PhaseSpacePosition
        self.phase_space_position = self._create_gala_phase_space()

    def _create_gala_phase_space(self):
        """Convert to Gala PhaseSpacePosition format."""
        # Gala expects shape (3, N) for positions and velocities
        pos = self.positions.T * u.kpc  # Assuming NEMO units are kpc
        vel = self.velocities.T * u.km/u.s  # Assuming NEMO velocities are km/s

        return gala_dynamics.PhaseSpacePosition(pos=pos, vel=vel)

    def __repr__(self):
        return (f"NemoData(particles={self.particle_count}, "
                f"time={self.time}, shape={self.positions.shape})")


def read_nemo(filename, timestep=0):
    """
    Read NEMO file and return particle data.

    Parameters
    ----------
    filename : str
        Path to NEMO data file
    timestep : int, optional
        Which timestep to extract (default: 0)

    Returns
    -------
    NemoData
        Container with particle positions, velocities, masses and Gala format

    Examples
    --------
    >>> data = read_nemo("simulation.dat")
    >>> print(data.particle_count)
    100000
    >>> orbit = potential.integrate_orbit(data.phase_space_position, ...)
    """
    nemo_binary_location = get_nemo_binary_path()

    falcon_converted_data_output = convert_data_using_falcon(nemo_binary_location, filename)

    particle_data = parse_converted_falcon_output(falcon_converted_data_output, timestep)

    return create_nemo_data(particle_data)


def get_nemo_binary_path():
    """
    Get path to NEMO TSF binary from environment variable.

    Returns
    -------
    str
        Path to tsf executable

    Raises
    ------
    EnvironmentError
        If NEMO_PATH not set
    """
    if 'NEMO_PATH' not in os.environ:
        raise EnvironmentError(
            "NEMO_PATH environment variable not set. "
            "Set it to your NEMO installation directory: "
            "export NEMO_PATH=/path/to/nemo"
        )

    nemo_base_path = os.environ['NEMO_PATH']
    tsf_path = os.path.join(nemo_base_path, 'bin', 'tsf')

    return tsf_path


def convert_data_using_falcon(nemo_binary_location, filename):
    """
    Run NEMO TSF command to convert binary data to text format.

    Parameters
    ----------
    nemo_binary_location : str
        Path to TSF executable
    filename : str
        NEMO data file to convert

    Returns
    -------
    str
        TSF command output
    """
    command = [nemo_binary_location, filename, "allline=true"]

    result = subprocess.run(command, capture_output=True, text=True, check=True)

    return result.stdout


def parse_converted_falcon_output(tsf_output, timestep):
    """
    Extract particle arrays from TSF output.

    Parameters
    ----------
    tsf_output : str
        Raw TSF command output
    timestep : int
        Which timestep to extract

    Returns
    -------
    dict
        Dictionary with positions, velocities, masses, time, particle_count
    """
    lines = tsf_output.split('\n')

    # Extract basic simulation info
    particle_count, simulation_time = extract_simulation_info(lines)

    # Extract particle data arrays
    positions = extract_particle_array(lines, 'Position', particle_count, 3)
    velocities = extract_particle_array(lines, 'Velocity', particle_count, 3)
    masses = extract_particle_array(lines, 'Mass', particle_count, 1)

    return {
        'positions': positions,
        'velocities': velocities,
        'masses': masses,
        'time': simulation_time,
        'particle_count': particle_count
    }


def extract_simulation_info(lines):
    """Extract particle count and simulation time from TSF output."""
    particle_count = None
    simulation_time = None

    for line in lines:
        if 'int Nobj' in line:
            particle_count = int(line.split()[-1])
        elif 'double Time' in line:
            simulation_time = float(line.split()[-1])

    if particle_count is None:
        raise ValueError("Could not find particle count in TSF output")

    return particle_count, simulation_time


def extract_particle_array(lines, array_name, particle_count, dimensions):
    """
    Extract numerical array from TSF output.

    Parameters
    ----------
    lines : list
        TSF output split into lines
    array_name : str
        Name of array to extract ('Position', 'Velocity', 'Mass')
    particle_count : int
        Expected number of particles
    dimensions : int
        Array dimensions (3 for pos/vel, 1 for mass)

    Returns
    -------
    np.ndarray
        Extracted array data
    """
    # Find where this array starts
    start_line = find_array_start_line(lines, array_name, particle_count)

    # Extract all numbers from this section
    numbers = extract_numbers_from_section(lines, start_line, array_name)

    # Reshape to proper dimensions
    return reshape_for_particles(numbers, particle_count, dimensions)


def find_array_start_line(lines, array_name, particle_count):
    """Find the line where a specific array starts."""
    search_pattern = f'{array_name}[{particle_count}]'

    for i, line in enumerate(lines):
        if search_pattern in line:
            return i

    raise ValueError(f"Could not find {array_name} array in TSF output")


def extract_numbers_from_section(lines, start_line, array_name):
    """Extract all numbers from an array section."""
    numbers = []

    for i in range(start_line, len(lines)):
        line = lines[i].strip()

        # Stop when we hit the next section or end
        if should_stop_parsing(line, array_name):
            break

        # Skip the header line, but extract numbers if they're on the same line
        if f'{array_name}[' in line:
            parts = line.split()
            start_idx = next(i for i, part in enumerate(parts) if ']' in part) + 1
            numbers.extend([float(x) for x in parts[start_idx:]])
            continue

        # Extract numbers from data lines
        if line and not is_header_line(line):
            clean_line = line.replace('. . .', '')  # Handle continuation markers
            parts = clean_line.split()

            for part in parts:
                try:
                    numbers.append(float(part))
                except ValueError:
                    continue  # Skip non-numeric entries

    return numbers


def should_stop_parsing(line, array_name):
    """Check if we should stop parsing this array section."""
    if line == 'tes':
        return True
    if line.startswith(('float ', 'double ')) and array_name not in line:
        return True
    return False


def is_header_line(line):
    """Check if line is a header rather than data."""
    return line.startswith(('int ', 'double ', 'float ', 'char ', 'set ', 'tes'))


def reshape_for_particles(numbers, particle_count, dimensions):
    """Reshape flat number list into proper particle array."""
    if dimensions == 1:
        return np.array(numbers[:particle_count])
    else:
        total_expected = particle_count * dimensions
        numbers = numbers[:total_expected]
        return np.array(numbers).reshape(particle_count, dimensions)


def create_nemo_data(particle_data):
    """Package particle data into NemoData container."""
    return NemoData(
        positions=particle_data['positions'],
        velocities=particle_data['velocities'],
        masses=particle_data['masses'],
        time=particle_data['time'],
        particle_count=particle_data['particle_count']
    )