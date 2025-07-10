"""
Import Management Module

Handles all the standard imports and setup needed for stellar stream analysis.
This eliminates the need to copy-paste large import blocks in every notebook.
"""

import sys
import warnings


def setup_imports(interactive_plots=True, verbose=True):
    """
    Set up all standard imports for stellar stream analysis.

    This function imports and configures all the commonly used libraries,
    sets up default parameters, and returns them as a dictionary for easy access.

    Parameters
    ----------
    interactive_plots : bool, optional
        Whether to include plotly for interactive plotting (default: True)
    verbose : bool, optional
        Whether to print import status (default: True)

    Returns
    -------
    dict
        Dictionary containing all imported modules and commonly used objects

    Examples
    --------
    >>> imports = setup_imports()
    >>> u = imports['u']  # astropy units
    >>> plt = imports['plt']  # matplotlib
    >>> coord = imports['coord']  # astropy coordinates
    """

    if verbose:
        print("Setting up stellar stream analysis environment...")

    # Dictionary to store all imports
    modules = {}

    # =============================================================================
    # MATHEMATICAL AND PLOTTING TOOLS
    # =============================================================================
    if verbose:
        print("  Importing mathematical and plotting tools...")

    import numpy as np
    import pandas as pd
    from scipy.optimize import minimize

    # Standard plotting
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib import colors
    from mpl_toolkits import mplot3d

    modules.update({
        'sys': sys,
        'np': np,
        'numpy': np,
        'pd': pd,
        'pandas': pd,
        'minimize': minimize,
        'matplotlib': matplotlib,
        'plt': plt,
        'colors': colors,
        'mplot3d': mplot3d
    })

    # Interactive plotting (optional)
    if interactive_plots:
        try:
            import plotly.express as px
            modules['px'] = px
            if verbose:
                print("    ✓ Plotly available for interactive plots")
        except ImportError:
            if verbose:
                print("    ⚠ Plotly not available - interactive plots disabled")

    # =============================================================================
    # ASTRONOMY COORDINATES AND UNITS
    # =============================================================================
    if verbose:
        print("  Importing astronomy libraries...")

    import astropy.units as u
    from astropy.table import Table
    from astropy.coordinates import Angle, SkyCoord
    import astropy.coordinates as coord

    modules.update({
        'u': u,
        'units': u,
        'Table': Table,
        'Angle': Angle,
        'SkyCoord': SkyCoord,
        'coord': coord
    })

    # =============================================================================
    # GALA - GALACTIC DYNAMICS LIBRARY
    # =============================================================================
    if verbose:
        print("  Importing Gala galactic dynamics...")

    import gala.potential as gala_potential
    import gala.dynamics as gala_dynamics
    import gala.integrate as gi
    from gala.dynamics import mockstream as ms
    from gala.units import galactic
    import gala

    modules.update({
        'gala_potential': gala_potential,
        'gp': gala_potential,  # Common shorthand
        'gala_dynamics': gala_dynamics,
        'gd': gala_dynamics,  # Common shorthand
        'gi': gi,
        'ms': ms,
        'mockstream': ms,
        'galactic': galactic,
        'gala': gala
    })

    # =============================================================================
    # DATA QUERY TOOLS (OPTIONAL)
    # =============================================================================
    if verbose:
        print("  Setting up data query tools...")

    # Check if we're in Colab
    IN_COLAB = 'google.colab' in sys.modules
    modules['IN_COLAB'] = IN_COLAB

    # Try to import astroquery
    try:
        from astroquery.gaia import Gaia
        from astroquery.vizier import Vizier
        ASTROQUERY_AVAILABLE = True
        modules.update({
            'Gaia': Gaia,
            'Vizier': Vizier,
            'ASTROQUERY_AVAILABLE': True
        })
        if verbose:
            print("    ✓ Astroquery available for data queries")
    except ImportError:
        ASTROQUERY_AVAILABLE = False
        modules['ASTROQUERY_AVAILABLE'] = False
        if verbose:
            print("    ⚠ Astroquery not available - data queries disabled")

    # =============================================================================
    # SETUP DEFAULT PARAMETERS
    # =============================================================================
    if verbose:
        print("  Configuring default parameters...")

    # Set default Astropy Galactocentric frame parameters (v4.0 standards)
    _ = coord.galactocentric_frame_defaults.set('v4.0')

    # Suppress common warnings for cleaner output
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='astropy')

    if verbose:
        print("✓ Setup complete!")
        print(f"  Running in Colab: {IN_COLAB}")
        print(f"  Astroquery available: {ASTROQUERY_AVAILABLE}")
        print(f"  Interactive plots: {interactive_plots}")

    return modules


def quick_imports():
    """
    Quick import setup with minimal output.

    Returns
    -------
    dict
        Dictionary of imported modules
    """
    return setup_imports(verbose=False)


# For backwards compatibility and convenience
def get_standard_imports():
    """Legacy function name - use setup_imports() instead."""
    warnings.warn("get_standard_imports() is deprecated, use setup_imports()",
                  DeprecationWarning, stacklevel=2)
    return setup_imports()


# Convenience function to inject imports into global namespace
def inject_imports(globals_dict=None):
    """
    Inject all imports directly into the global namespace.

    WARNING: This modifies the global namespace. Use with caution.
    Generally better to use: imports = setup_imports()

    Parameters
    ----------
    globals_dict : dict, optional
        Global namespace to inject into (default: caller's globals)
    """
    if globals_dict is None:
        # Get caller's globals
        import inspect
        frame = inspect.currentframe().f_back
        globals_dict = frame.f_globals

    imports = setup_imports(verbose=False)
    globals_dict.update(imports)

    print("All imports injected into global namespace")
    print("Available: u, np, plt, coord, gp, gd, ms, etc.")