"""
Globular Cluster Configuration Module

This module provides pre-defined globular cluster parameters and utilities
for creating cluster objects with proper coordinate transformations.
"""

import astropy.units as u
import astropy.coordinates as coord
import gala.dynamics as gala_dynamics

# Pre-defined cluster configurations
CLUSTER_CONFIGS = {
    "ngc6569": {
        "name": "NGC 6569",
        "ra": 273.412 * u.degree,
        "dec": -31.827 * u.degree,
        "distance": 10.5 * u.kpc,
        "pm_ra_cosdec": -4.125 * u.mas / u.yr,
        "pm_dec": -7.354 * u.mas / u.yr,
        "radial_velocity": -49.82 * u.km / u.s,  # Modified RV for velocity dispersion
        "mass": 2.3E5 * u.Msun,
        "scale_radius": 4 * u.pc,
        "source": "Vasiliev et al. 2021, modified RV"
    },

    "pal5": {
        "name": "Palomar 5",
        "ra": 229.019 * u.degree,
        "dec": -0.121 * u.degree,
        "distance": 21.94 * u.kpc,
        "pm_ra_cosdec": -2.730 * u.mas / u.yr,
        "pm_dec": -2.654 * u.mas / u.yr,
        "radial_velocity": -58.60 * u.km / u.s,
        "mass": 1.3E4 * u.Msun,
        "scale_radius": 4 * u.pc,
        "source": "Baumgardt & Vasiliev 2021"
    }
}


class Cluster:
    """
    Represents a globular cluster with observational properties and coordinate transformations.

    This class handles the coordinate transformations from observational
    (RA/Dec) coordinates to Galactocentric coordinates needed for orbital integration.
    """

    def __init__(self, name, ra, dec, distance, pm_ra_cosdec, pm_dec,
                 radial_velocity, mass, scale_radius=4 * u.pc, source=None):
        """
        Initialize a globular cluster.

        Parameters
        ----------
        name : str
            Name of the cluster
        ra : astropy.units.Quantity
            Right ascension
        dec : astropy.units.Quantity
            Declination
        distance : astropy.units.Quantity
            Distance to cluster
        pm_ra_cosdec : astropy.units.Quantity
            Proper motion in RA (includes cos(dec) factor)
        pm_dec : astropy.units.Quantity
            Proper motion in declination
        radial_velocity : astropy.units.Quantity
            Heliocentric radial velocity
        mass : astropy.units.Quantity
            Total cluster mass
        scale_radius : astropy.units.Quantity, optional
            Scale radius for cluster potential (default: 4 pc)
        source : str, optional
            Data source reference
        """
        self.name = name
        self.ra = ra
        self.dec = dec
        self.distance = distance
        self.pm_ra_cosdec = pm_ra_cosdec
        self.pm_dec = pm_dec
        self.radial_velocity = radial_velocity
        self.mass = mass
        self.scale_radius = scale_radius
        self.source = source

        # Create coordinate objects
        self._setup_coordinates()

    def _setup_coordinates(self):
        """Set up coordinate transformations."""
        # Create SkyCoord object in ICRS frame
        self.skycoord = coord.SkyCoord(
            ra=self.ra,
            dec=self.dec,
            distance=self.distance,
            pm_ra_cosdec=self.pm_ra_cosdec,
            pm_dec=self.pm_dec,
            radial_velocity=self.radial_velocity
        )

        # Transform to Galactocentric coordinates
        self.galactocentric = self.skycoord.transform_to(coord.Galactocentric)

        # Create Gala PhaseSpacePosition for orbit integration
        self.phase_space_position = gala_dynamics.PhaseSpacePosition(self.galactocentric.data)

    @classmethod
    def from_config(cls, cluster_name):
        """
        Create a cluster from pre-defined configuration.

        Parameters
        ----------
        cluster_name : str
            Name of pre-defined cluster ('ngc6569', 'pal5')

        Returns
        -------
        Cluster
            Initialized cluster object

        Examples
        --------
        >>> cluster = Cluster.from_config("ngc6569")
        >>> print(cluster.name)
        NGC 6569
        """
        if cluster_name.lower() not in CLUSTER_CONFIGS:
            available = list(CLUSTER_CONFIGS.keys())
            raise ValueError(f"Unknown cluster '{cluster_name}'. Available: {available}")

        config = CLUSTER_CONFIGS[cluster_name.lower()]
        return cls(**config)

    def __repr__(self):
        """String representation of the cluster."""
        return (f"Cluster(name='{self.name}', "
                f"ra={self.ra:.3f}, dec={self.dec:.3f}, "
                f"distance={self.distance:.1f}, mass={self.mass:.1e})")

    def info(self):
        """Print detailed cluster information."""
        print(f"Cluster: {self.name}")
        print(f"Coordinates: RA={self.ra:.3f}, Dec={self.dec:.3f}")
        print(f"Distance: {self.distance:.2f}")
        print(f"Proper motion: μ_α*={self.pm_ra_cosdec:.3f}, μ_δ={self.pm_dec:.3f}")
        print(f"Radial velocity: {self.radial_velocity:.2f}")
        print(f"Mass: {self.mass:.1e}")
        if self.source:
            print(f"Source: {self.source}")

        print(f"\nGalactocentric coordinates:")
        print(f"X: {self.galactocentric.x:.2f}")
        print(f"Y: {self.galactocentric.y:.2f}")
        print(f"Z: {self.galactocentric.z:.2f}")


def get_cluster(cluster_name):
    """
    Convenience function to get a cluster by name.

    Parameters
    ----------
    cluster_name : str
        Name of cluster ('ngc6569', 'pal5')

    Returns
    -------
    Cluster
        Cluster object
    """
    return Cluster.from_config(cluster_name)


def list_available_clusters():
    """List all available pre-defined clusters."""
    print("Available clusters:")
    for name, config in CLUSTER_CONFIGS.items():
        print(f"  {name}: {config['name']}")