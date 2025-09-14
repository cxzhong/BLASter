# BLASter Python Interface

A modern, user-friendly Python interface for the BLASter LLL lattice reduction library.

## Features

- **NumPy Integration**: Work directly with numpy arrays (row vectors)
- **Comprehensive Results**: Get reduced basis, transformation matrix, and quality metrics
- **Multiple Algorithms**: LLL and BKZ reduction with customizable parameters
- **Performance Tracking**: Built-in timing and iteration counting
- **Quality Assessment**: Root Hermite Factor, slope, and other reduction metrics

## Quick Start

```python
import numpy as np
import blaster

# Create a lattice basis (each row is a lattice vector)
basis = np.array([
    [1, 2, 3],
    [2, 3, 4], 
    [3, 4, 6]
])

# Perform LLL reduction
result = blaster.lll_reduce(basis)

print("Original basis:")
print(basis)
print("\nLLL-reduced basis:")
print(result.reduced_basis)
print(f"\nRoot Hermite Factor: {result.rhf:.6f}")
print(f"Iterations: {result.time_profile.num_iterations}")
print(f"Transformation verified: {result.verify_transformation()}")
```

## Main Functions

### `lll_reduce(basis, **kwargs)`

Primary function for LLL lattice reduction.

**Parameters:**
- `basis` (array_like): Input lattice basis as 2D array (rows = vectors)
- `delta` (float): LLL parameter ∈ (0.25, 1), default 0.99
- `block_size` (int): Block size for segmented reduction
- `cores` (int): Number of parallel cores to use
- `use_seysen` (bool): Use Seysen's reduction algorithm
- `verbose` (bool): Print progress information

**Returns:**
- `LLLResult`: Object with reduced basis, transformation matrix, and statistics

### `bkz_reduce(basis, beta, tours=1, **kwargs)`

BKZ (Block Korkine-Zolotarev) reduction.

**Parameters:**
- `basis` (array_like): Input lattice basis
- `beta` (int): BKZ block size parameter  
- `tours` (int): Number of BKZ tours to perform
- Additional parameters same as `lll_reduce`

### Convenience Functions

- `lll(basis, **kwargs)`: Returns just the reduced basis (not full result object)
- `bkz(basis, beta, **kwargs)`: Returns just the BKZ-reduced basis
- `estimate_reduction_quality(basis)`: Estimate quality metrics before reduction

## LLLResult Object

The result object provides comprehensive information about the reduction:

```python
result = blaster.lll_reduce(basis)

# Access results
result.reduced_basis        # The LLL-reduced lattice basis
result.transformation      # Unimodular transformation matrix U
result.original_basis      # Original input basis
result.time_profile       # Timing and iteration information

# Quality metrics
result.rhf                # Root Hermite Factor
result.slope              # Basis quality slope
result.potential          # Lattice potential
result.reduction_factor   # Determinant ratio (should be 1)

# Verification
result.verify_transformation()  # Check if U @ original = reduced
```

## Example Applications

### Cryptographic Lattices

```python
# Knapsack lattice for subset sum problems
n = 6
weights = [15, 92, 17, 38, 52, 78]
M = 200

basis = np.zeros((n + 1, n + 1), dtype=int)
for i in range(n):
    basis[i, i] = 1
    basis[i, n] = weights[i]
basis[n, n] = M

result = blaster.lll_reduce(basis, delta=0.99)
print(f"Reduced lattice RHF: {result.rhf:.6f}")
```

### Linear System Lattices

```python
# Find small integer solutions to Ax = b
A = np.array([[2, 3, 5], [1, 4, 6], [3, 1, 2]])
n, m = A.shape

# Construct lattice for small solutions
lattice = np.block([
    [np.eye(m), A.T],
    [np.zeros((n, m)), 100 * np.eye(n)]
])

result = blaster.lll_reduce(lattice)
# Shortest vector gives small solution
norms = np.linalg.norm(result.reduced_basis, axis=1)
shortest = result.reduced_basis[np.argmin(norms)]
print(f"Small solution vector: {shortest}")
```

### Algorithm Comparison

```python
import blaster

basis = generate_random_lattice(dimension=50, bits=20)

# Compare LLL vs BKZ
lll_result = blaster.lll_reduce(basis, verbose=False)
bkz_result = blaster.bkz_reduce(basis, beta=10, tours=3, verbose=False)

print(f"LLL RHF: {lll_result.rhf:.6f}")
print(f"BKZ-10 RHF: {bkz_result.rhf:.6f}")  # Should be better
print(f"LLL time: {lll_result.time_profile.total_time:.3f}s")
print(f"BKZ time: {bkz_result.time_profile.total_time:.3f}s")
```

## Performance Tips

1. **Use integer matrices**: BLASter works with integer lattices for best performance
2. **Parallel processing**: Set `cores` parameter to use multiple CPU cores  
3. **Block size tuning**: Adjust `block_size` for memory/speed trade-off
4. **BKZ parameters**: Higher `beta` gives better reduction but takes more time
5. **Delta parameter**: Values closer to 1.0 give better reduction

## Advanced Usage

```python
# Custom reduction with all parameters
result = blaster.lll_reduce(
    basis,
    delta=0.999,           # High-quality reduction
    block_size=64,         # Large blocks for big lattices  
    cores=4,               # Use 4 CPU cores
    use_seysen=True,       # Alternative reduction algorithm
    verbose=True           # Show progress
)

# Quality estimation before reduction
quality = blaster.estimate_reduction_quality(basis)
print(f"Before: RHF={quality['rhf']:.6f}, condition={quality['condition_number']:.2f}")

# Check if already reduced
if blaster.is_lll_reduced(basis, delta=0.99):
    print("Basis is already LLL-reduced!")
```

For more examples, see `examples/demo.py`.