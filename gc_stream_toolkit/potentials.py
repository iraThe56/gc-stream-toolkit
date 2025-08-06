"""
Galactic Potential Configuration Module

Pre-defined galactic potential configurations for stellar stream simulations.
"""

import astropy.units as u
import gala.potential as gala_potential
from gala.units import galactic


def _create_milky_way_composite():
    """Create standard 3-component Milky Way potential."""
    potential = gala_potential.CCompositePotential()

    potential['bar'] = gala_potential.LongMuraliBarPotential(
        m=2E10*u.Msun,
        a=4*u.kpc, b=0.5*u.kpc, c=0.5*u.kpc,
        alpha=25*u.degree,
        units=galactic)

    potential['disk'] = gala_potential.MiyamotoNagaiPotential(
        m=5E10*u.Msun,
        a=3.*u.kpc, b=280.*u.pc,
        units=galactic)

    potential['halo'] = gala_potential.NFWPotential(
        m=6E11*u.Msun,
        r_s=20.*u.kpc,
        units=galactic)

    return potential


def _create_gala_example():
    """Create simple 2-component Gala example potential."""
    potential = gala_potential.CCompositePotential()

    potential['disk'] = gala_potential.MiyamotoNagaiPotential(
        m=6E10*u.Msun,
        a=3.5*u.kpc, b=280*u.pc,
        units=galactic)

    potential['halo'] = gala_potential.NFWPotential(
        m=7E11*u.Msun,
        r_s=15*u.kpc,
        units=galactic)

    return potential


def _create_milky_way_barred():
    """Create barred Milky Way potential with rotating frame."""
    potential = _create_milky_way_composite()

    bar_rotation_speed = 42. * u.km/u.s/u.kpc
    rotating_frame = gala_potential.ConstantRotatingFrame(
        Omega=[0, 0, bar_rotation_speed.value] * bar_rotation_speed.unit,
        units=galactic)

    return gala_potential.Hamiltonian(potential=potential, frame=rotating_frame)


# Configuration dictionary
POTENTIAL_CONFIGS = {
    "gala_example": {
        "name": "Gala Example",
        "description": "Simple 2-component MW (disk + halo)",
        "type": "CCompositePotential",
        "factory": _create_gala_example,
        "source": "Standard Gala documentation example"
    },
    "milky_way_composite": {
        "name": "Milky Way Composite",
        "description": "3-component MW (bar + disk + halo)",
        "type": "CCompositePotential",
        "factory": _create_milky_way_composite,
        "source": "Standard galactic components"
    },
    "milky_way_barred": {
        "name": "Milky Way Barred",
        "description": "3-component MW with rotating bar frame",
        "type": "Hamiltonian",
        "factory": _create_milky_way_barred,
        "source": "Composite potential + 42 km/s/kpc bar rotation"
    }
}



def get_potential(potential_name):
    """
    Get a pre-configured galactic potential by name.

    Parameters
    ----------
    potential_name : str
        Name of potential configuration ('milky_way_composite', 'milky_way_barred')

    Returns
    -------
    gala potential object
        Either CCompositePotential or Hamiltonian depending on configuration

    Examples
    --------
    >>> potential = get_potential("milky_way_composite")
    >>> hamiltonian = get_potential("milky_way_barred")
    """
    if potential_name.lower() not in POTENTIAL_CONFIGS:
        available = list(POTENTIAL_CONFIGS.keys())
        raise ValueError(f"Unknown potential '{potential_name}'. Available: {available}")

    config = POTENTIAL_CONFIGS[potential_name.lower()]
    return config['factory']()

