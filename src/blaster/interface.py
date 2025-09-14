"""
High-level Python interface for BLASter LLL library.

This module provides a user-friendly interface that works directly with numpy matrices,
handling the conversion between row/column formats and providing sensible defaults.
"""

import numpy as np

from .blaster import TimeProfile
from .blaster import reduce as _blaster_reduce
from .stats import potential, rhf, slope


class LLLResult:
    """
    Result of LLL reduction containing the reduced basis, transformation matrix, and statistics.
    """

    def __init__(
        self,
        reduced_basis: np.ndarray,
        transformation: np.ndarray,
        time_profile: TimeProfile,
        original_basis: np.ndarray,
    ):
        self.reduced_basis = reduced_basis
        self.transformation = transformation
        self.time_profile = time_profile
        self.original_basis = original_basis

        # Compute final R matrix for statistics
        R = np.linalg.qr(reduced_basis.T, mode="r")  # QR on column vectors
        self._rhf = rhf(np.diag(R))
        self._slope = slope(np.diag(R))
        self._potential = potential(np.diag(R))

    @property
    def rhf(self) -> float:
        """Root Hermite Factor of the reduced basis."""
        return self._rhf

    @property
    def slope(self) -> float:
        """Slope of the log profile of the reduced basis."""
        return self._slope

    @property
    def potential(self) -> float:
        """Potential of the reduced basis."""
        return self._potential

    @property
    def reduction_factor(self) -> float:
        """Ratio of original to reduced basis determinant (should be 1 for LLL)."""
        orig_det = abs(np.linalg.det(self.original_basis))
        red_det = abs(np.linalg.det(self.reduced_basis))
        return orig_det / red_det if red_det != 0 else float("inf")

    @property
    def orthogonality_defect(self) -> float:
        """
        Orthogonality defect of the reduced basis.
        
        The orthogonality defect measures how far the basis is from being orthogonal.
        It's defined as the ratio of the product of basis vector norms to the volume.
        A perfectly orthogonal basis has orthogonality defect 1.
        """
        # Calculate norms of basis vectors
        norms = np.linalg.norm(self.reduced_basis, axis=1)
        product_of_norms = np.prod(norms)
        
        # Calculate volume (absolute value of determinant)
        volume = abs(np.linalg.det(self.reduced_basis))
        
        if volume == 0:
            return float("inf")
        
        return product_of_norms / volume

    def verify_transformation(self) -> bool:
        """Verify that the unimodular transformation is correct."""
        try:
            # Check if U @ original_basis = reduced_basis
            computed = self.transformation @ self.original_basis
            return np.allclose(computed, self.reduced_basis, atol=1e-10)
        except Exception:
            return False

    def __repr__(self) -> str:
        return (
            f"LLLResult(dimension={self.reduced_basis.shape}, "
            f"rhf={self.rhf:.6f}, slope={self.slope:.6f}, "
            f"iterations={self.time_profile.num_iterations})"
        )


def lll_reduce(
    basis,
    delta=0.99,
    block_size=None,
    cores=None,
    use_seysen=False,
    verbose=True,
    **kwargs,
):
    """
    Perform LLL reduction on a lattice basis using numpy arrays.

    This is the main high-level interface for lattice reduction. It handles
    the conversion between row vectors (standard numpy convention) and
    column vectors (internal BLASter format).

    Args:
        basis (array_like): Input lattice basis as a 2D array where each
            row is a lattice vector. Shape should be (n_vectors, dimension).
        delta (float, optional): LLL parameter, should be in (0.25, 1).
            Higher values give better reduction. Default: 0.99.
        block_size (int, optional): Block size for segmented reduction.
            If None, uses automatic selection. Default: None.
        cores (int, optional): Number of cores to use for parallel reduction.
            If None, uses all available cores. Default: None.
        use_seysen (bool, optional): Whether to use Seysen's reduction
            algorithm instead of standard size reduction. Default: False.
        verbose (bool, optional): Whether to print progress information.
            Default: True.

    Returns:
        LLLResult: Object containing the reduced basis, transformation matrix,
            reduction quality metrics, and timing information.

    Raises:
        ValueError: If the input basis is invalid (wrong shape, singular, etc.).
        RuntimeError: If the reduction algorithm fails.

    Example:
        >>> import numpy as np
        >>> import blaster
        >>> basis = np.array([[1, 2], [2, 3]])
        >>> result = blaster.lll_reduce(basis)
        >>> print(result.reduced_basis)
        [[ 0 -1]
         [ 1  0]]
    """
    # Convert to numpy array and validate
    B = np.asarray(basis)
    if B.ndim != 2:
        raise ValueError("Basis must be a 2D array")
    if B.shape[0] == 0 or B.shape[1] == 0:
        raise ValueError("Basis cannot be empty")

    # Convert to integer type (required by BLASter core)
    try:
        B = B.astype(int)
    except (ValueError, OverflowError) as e:
        raise ValueError("Basis must contain integer values") from e

    # Check for reasonable condition number to avoid numerical issues
    try:
        B_float = B.astype(float)
        det = np.linalg.det(B_float @ B_float.T)
        if abs(det) < 1e-12:
            raise ValueError("Basis appears to be singular or nearly singular")
    except np.linalg.LinAlgError as e:
        raise ValueError("Basis is singular or has numerical issues") from e

    # Convert to column vector format (transpose)
    B = B.T.copy()

    # Set up parameters
    reduction_params = {
        "delta": float(delta),
        "use_seysen": bool(use_seysen),
        "verbose": bool(verbose),
    }

    if block_size is not None:
        reduction_params["lll_size"] = int(block_size)

    # Pass through any additional BKZ parameters
    if "beta" in kwargs:
        reduction_params["beta"] = int(kwargs["beta"])
    if "bkz_tours" in kwargs:
        reduction_params["bkz_tours"] = int(kwargs["bkz_tours"])
    if cores is not None:
        from . import blaster as _blaster

        _blaster.set_num_cores(int(cores))

    try:
        # Perform the reduction
        U, B_reduced, time_profile = _blaster_reduce(B, **reduction_params)

        # Convert back to row vector format
        B_reduced = B_reduced.T

        # Create result object
        return LLLResult(
            reduced_basis=B_reduced,
            transformation=U.T,  # Also transpose for consistency
            original_basis=np.asarray(basis),
            time_profile=time_profile,
        )
    except Exception as e:
        raise RuntimeError(f"LLL reduction failed: {e}") from e


def lll_reduce_basis(basis: np.ndarray, **kwargs) -> np.ndarray:
    """
    Convenience function that returns only the reduced basis.

    Parameters
    ----------
    basis : np.ndarray
        The lattice basis to reduce.
    **kwargs
        Same parameters as lll_reduce()

    Returns
    -------
    np.ndarray
        The LLL-reduced basis.
    """
    result = lll_reduce(basis, **kwargs)
    return result.reduced_basis


def bkz_reduce(basis: np.ndarray, beta: int, tours: int = 1, **kwargs) -> LLLResult:
    """
    Convenience function for BKZ reduction.

    Parameters
    ----------
    basis : np.ndarray
        The lattice basis to reduce.
    beta : int
        BKZ block size parameter.
    tours : int, default=1
        Number of BKZ tours to perform.
    **kwargs
        Additional parameters (same as lll_reduce).

    Returns
    -------
    LLLResult
        Object containing the reduced basis, transformation matrix, and statistics.
    """
    # BKZ is enabled by passing beta parameter to the main reduce function
    return lll_reduce(basis, beta=beta, bkz_tours=tours, **kwargs)


def estimate_reduction_quality(
    basis: np.ndarray, row_vectors: bool = True
) -> dict[str, float]:
    """
    Estimate the quality of a lattice basis without performing reduction.

    Parameters
    ----------
    basis : np.ndarray
        The lattice basis to analyze.
    row_vectors : bool, default=True
        Whether the basis uses row vectors or column vectors.

    Returns
    -------
    dict
        Dictionary containing quality metrics: rhf, slope, potential, condition_number.
    """
    if row_vectors:
        B = basis.T
    else:
        B = basis.copy()

    # Compute QR decomposition
    R = np.linalg.qr(B, mode="r")
    diag_R = np.diag(R)

    # Condition number
    cond_num = np.linalg.cond(basis.astype(float))

    return {
        "rhf": rhf(diag_R),
        "slope": slope(diag_R),
        "potential": potential(diag_R),
        "condition_number": cond_num,
        "log_volume": np.sum(np.log(np.abs(diag_R))),
    }


# Convenient aliases for common use cases
reduce_lattice = lll_reduce
lll = lll_reduce_basis


def bkz(basis, beta, **kwargs):
    return bkz_reduce(basis, beta, **kwargs).reduced_basis


def demo_usage():
    """
    Demonstrate the usage of the BLASter interface.
    """
    print("BLASter LLL Library - Python Interface Demo")
    print("=" * 45)

    # Create a simple example basis
    basis = np.array([[1, 1, 1], [-1, 0, 2], [3, 5, 6]])

    print(f"Original basis:\n{basis}")

    # Analyze original basis
    original_quality = estimate_reduction_quality(basis)
    print("\nOriginal basis quality:")
    print(f"  RHF: {original_quality['rhf']:.6f}")
    print(f"  Slope: {original_quality['slope']:.6f}")
    print(f"  Condition number: {original_quality['condition_number']:.2f}")

    # Perform LLL reduction
    print("\nPerforming LLL reduction...")
    result = lll_reduce(basis, verbose=True)

    print(f"\nReduced basis:\n{result.reduced_basis}")
    print(f"\nTransformation matrix:\n{result.transformation}")

    print("\nReduction results:")
    print(f"  RHF: {result.rhf:.6f}")
    print(f"  Slope: {result.slope:.6f}")
    print(f"  Iterations: {result.time_profile.num_iterations}")
    print(f"  Transformation verified: {result.verify_transformation()}")

    print("\nTime profile:")
    print(result.time_profile)


if __name__ == "__main__":
    demo_usage()
