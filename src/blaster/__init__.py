"""
BLASter: A proof of concept of an LLL-like lattice reduction algorithm

BLASter is a lattice reduction algorithm that uses:
- parallelization,
- segmentation,
- Seysen's reduction instead of size reduction, and
- a linear algebra library.

This is a proof of concept implementation focusing on demonstrating
speed ups that are possible in lattice reduction software.
"""

__version__ = "0.1.0"

from .lattice_io import *

# Import main classes and functions
from .size_reduction import (
    is_lll_reduced,
    is_weakly_lll_reduced,
    seysen_reduce,
    size_reduce,
)
from .stats import get_profile, potential, rhf, slope

try:
    # Import the compiled Cython extension
    from blaster_core import (
        ZZ_right_matmul,
        block_bkz,
        block_deep_lll,
        block_lll,
        set_debug_flag,
        set_num_cores,
    )

    # Now import classes that depend on the extension
    from .blaster import TimeProfile, reduce

    # Import high-level interface
    from .interface import (
        LLLResult,
        bkz,
        bkz_reduce,
        estimate_reduction_quality,
        lll,
        lll_reduce,
        lll_reduce_basis,
        reduce_lattice,
    )

    __all__ = [
        # High-level interface (recommended)
        "lll_reduce",
        "lll_reduce_basis",
        "bkz_reduce",
        "LLLResult",
        "estimate_reduction_quality",
        "reduce_lattice",
        "lll",
        "bkz",
        # Low-level interface
        "TimeProfile",
        "reduce",
        "is_lll_reduced",
        "is_weakly_lll_reduced",
        "size_reduce",
        "seysen_reduce",
        "get_profile",
        "rhf",
        "slope",
        "potential",
        "set_debug_flag",
        "set_num_cores",
        "block_lll",
        "block_deep_lll",
        "block_bkz",
        "ZZ_right_matmul",
    ]
except ImportError as e:
    import warnings

    warnings.warn(
        f"Could not import blaster_core extension: {e}. "
        "The package may not be properly compiled. "
        "Try running 'pip install -e .' or 'make' to build the extension."
    )

    # Still export non-extension dependent functions
    __all__ = [
        "estimate_reduction_quality",
        "is_lll_reduced",
        "is_weakly_lll_reduced",
        "size_reduce",
        "seysen_reduce",
        "get_profile",
        "rhf",
        "slope",
        "potential",
    ]
