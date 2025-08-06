"""
Globular Cluster Data Configurations

Pre-defined observational parameters for globular clusters.
"""

import astropy.units as u

# Pre-defined cluster configurations
CLUSTER_CONFIGS = {
    "ngc6569": {
        "name": "NGC 6569",
        "ra": 273.412 * u.degree,
        "dec": -31.827 * u.degree,
        "distance": 10.53 * u.kpc,
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
    },
    "pal5_canonical": {
        "name": "Palomar 5 (Canonical)",
        "ra": 229 * u.degree,
        "dec": -0.124 * u.degree,
        "distance": 22.9 * u.kpc,
        "pm_ra_cosdec": -2.296 * u.mas / u.yr,
        "pm_dec": -2.257 * u.mas / u.yr,
        "radial_velocity": -58.7 * u.km / u.s,
        "mass": 1.3E4 * u.Msun,
        "scale_radius": 4 * u.pc,
        "source": "Odenkirchen+02, Bovy+16, Fritz+15 - canonical values"
    },

}