#!/usr/bin/env python3
"""
Example usage of the BLASter Python interface.

This script demonstrates how to use BLASter with numpy matrices
for lattice basis reduction.
"""

import numpy as np

import blaster


def main():
    print("BLASter LLL Library - Example Usage")
    print("=" * 40)

    # Example 1: Simple random integer lattice
    print("\n1. Random Integer Lattice")
    print("-" * 30)

    np.random.seed(42)  # For reproducible results
    basis = np.random.randint(-5, 6, size=(4, 4))
    print(f"Original basis (4x4):\n{basis}")

    # Basic LLL reduction
    result = blaster.lll_reduce(basis, verbose=False)
    print(f"\nLLL-reduced basis:\n{result.reduced_basis}")
    print(f"Root Hermite Factor: {result.rhf:.6f}")
    print(f"Iterations: {result.time_profile.num_iterations}")
    print(f"Transformation verified: {result.verify_transformation()}")

    # Example 2: Knapsack-type lattice
    print("\n\n2. Knapsack-type Lattice")
    print("-" * 30)

    # Create a knapsack lattice (common in cryptography)
    n = 6
    a = [15, 92, 17, 38, 52, 78]  # Knapsack weights
    M = 200  # Large number

    # Construct lattice basis
    basis = np.zeros((n + 1, n + 1), dtype=int)
    for i in range(n):
        basis[i, i] = 1
        basis[i, n] = a[i]
    basis[n, n] = M

    print(f"Knapsack lattice basis:\n{basis}")

    # Reduce with different parameters
    result = blaster.lll_reduce(basis, delta=0.99, block_size=32)
    print(f"\nReduced basis (first 3 rows):\n{result.reduced_basis[:3]}")
    print(f"RHF: {result.rhf:.6f}")

    # Example 3: Comparing algorithms
    print("\n\n3. Algorithm Comparison")
    print("-" * 30)

    # Create a challenging but well-conditioned lattice
    basis = np.array([[10, 2, 3, 1], [1, 12, 4, 2], [2, 1, 15, 3], [3, 2, 1, 20]])

    print(f"Original basis:\n{basis}")
    print(f"Determinant: {np.linalg.det(basis):.1f}")

    try:
        # LLL reduction
        lll_result = blaster.lll_reduce(basis)
        print(f"\nLLL result: RHF = {lll_result.rhf:.6f}")

        # BKZ reduction with small block size
        try:
            bkz_result = blaster.bkz_reduce(basis, beta=3, tours=2)
            print(f"BKZ-3 result: RHF = {bkz_result.rhf:.6f}")
        except Exception as e:
            print(f"BKZ failed: {e}")
    except Exception as e:
        print(f"Reduction failed: {e}")
        print("Skipping this example...")

    # Example 4: Working with existing numpy arrays
    print("\n\n4. Real-world Example")
    print("-" * 30)

    # Simulate a lattice from a linear Diophantine system Ax = b
    A = np.array([[2, 3, 5], [1, 4, 6], [3, 1, 2]], dtype=int)

    # Create lattice for finding small solutions
    n, m = A.shape
    lattice_basis = np.block(
        [
            [np.eye(m, dtype=int), A.T],
            [np.zeros((n, m), dtype=int), 100 * np.eye(n, dtype=int)],
        ]
    )

    print(f"Linear system lattice ({lattice_basis.shape[0]}x{lattice_basis.shape[1]}):")
    print(lattice_basis)

    # Quality before reduction
    quality_before = blaster.estimate_reduction_quality(lattice_basis)
    print("\nBefore reduction:")
    print(f"  RHF: {quality_before['rhf']:.6f}")
    print(f"  Condition number: {quality_before['condition_number']:.2f}")

    # Reduce the lattice
    result = blaster.lll_reduce(lattice_basis, delta=0.999, cores=2)
    print("\nAfter LLL reduction:")
    print(f"  RHF: {result.rhf:.6f}")
    print(f"  Iterations: {result.time_profile.num_iterations}")

    # Show the shortest vector
    norms = np.linalg.norm(result.reduced_basis, axis=1)
    shortest_idx = np.argmin(norms)
    print(
        f"  Shortest vector: {result.reduced_basis[shortest_idx]} (norm: {norms[shortest_idx]:.2f})"
    )

    # Example 5: Using convenience functions
    print("\n\n5. Convenience Functions")
    print("-" * 30)

    basis = np.random.randint(-3, 4, size=(3, 3))
    print(f"Original: det = {np.linalg.det(basis):.1f}")

    # Just get the reduced basis
    reduced = blaster.lll(basis)
    print(f"Reduced:  det = {np.linalg.det(reduced):.1f}")

    print("\nDemo completed!")


if __name__ == "__main__":
    main()
