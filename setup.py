"""
Custom setup.py for BLASter Cython extensions.

This setup.py is used by the modern pyproject.toml build system
to handle the custom Cython extension compilation that requires
special handling for Eigen and OpenMP.
"""

from pathlib import Path
from sys import argv, platform
from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy as np
import os
import shutil
import tarfile
import tempfile
import urllib.request


def download_eigen_if_needed():
    """
    Download and extract Eigen3 headers if not found in system.

    Returns:
        Path to Eigen3 headers directory.
    """
    EIGEN_VERSION = "3.4.0"
    EIGEN_URL = f"https://gitlab.com/libeigen/eigen/-/archive/{EIGEN_VERSION}/eigen-{EIGEN_VERSION}.tar.gz"

    # Build directory for Eigen headers
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    eigen_build_dir = build_dir / "eigen3"

    # Common Eigen installation paths to check first
    eigen_paths = [
        Path("eigen3"),  # Local installation
        Path("/usr/include/eigen3"),  # System installation (Ubuntu/Debian)
        Path("/usr/local/include/eigen3"),  # System installation (macOS/manual)
        Path.home() / ".local/include/eigen3",  # User installation
        Path("/opt/homebrew/include/eigen3"),  # macOS Homebrew (Apple Silicon)
        eigen_build_dir,  # Previously downloaded version
    ]

    # Check environment variable
    if "EIGEN3_INCLUDE_DIR" in os.environ:
        eigen_paths.insert(0, Path(os.environ["EIGEN3_INCLUDE_DIR"]))

    # Check conda environment
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        eigen_paths.append(Path(conda_prefix) / "include" / "eigen3")

    # Try to find existing Eigen installation
    for eigen_path in eigen_paths:
        if eigen_path.exists() and eigen_path.is_dir():
            # Check if this contains valid Eigen headers
            if (eigen_path / "Eigen" / "Core").exists():
                print(f"Found Eigen3 headers at: {eigen_path}")
                return eigen_path

    # No system Eigen found - download it
    print(f"Downloading Eigen {EIGEN_VERSION} for BLASter build...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tar_file = temp_path / f"eigen-{EIGEN_VERSION}.tar.gz"

        try:
            # Download the tar.gz file
            print(f"  Downloading from: {EIGEN_URL}")
            urllib.request.urlretrieve(EIGEN_URL, tar_file)

            # Extract the archive
            print(f"  Extracting to build directory...")
            with tarfile.open(tar_file, "r:gz") as tar:
                # Use filter='data' for Python 3.14+ compatibility
                try:
                    tar.extractall(temp_path, filter="data")
                except TypeError:
                    # Fallback for older Python versions that don't support filter
                    tar.extractall(temp_path)

            # Find the extracted directory
            extracted_dirs = [
                d
                for d in temp_path.iterdir()
                if d.is_dir() and d.name.startswith("eigen-")
            ]
            if not extracted_dirs:
                raise RuntimeError("Could not find extracted Eigen directory")

            extracted_dir = extracted_dirs[0]

            # Copy to build directory
            if eigen_build_dir.exists():
                shutil.rmtree(eigen_build_dir)
            shutil.copytree(extracted_dir, eigen_build_dir)

        except Exception as e:
            print(f"ERROR: Failed to download Eigen: {e}")
            print("Please install Eigen3 manually:")
            print("  - Ubuntu/Debian: sudo apt-get install libeigen3-dev")
            print("  - macOS: brew install eigen")
            print("  - Or set EIGEN3_INCLUDE_DIR environment variable")
            exit(1)

    print(f"  Eigen {EIGEN_VERSION} ready at: {eigen_build_dir}")
    return eigen_build_dir


def get_eigen_include_dirs():
    """Get include directories including numpy and Eigen3."""
    include_dirs = [np.get_include()]

    # Get Eigen headers (download if necessary)
    eigen_dir = download_eigen_if_needed()
    include_dirs.append(str(eigen_dir))

    return include_dirs


def get_compile_args():
    """Get platform-specific compile arguments."""
    # Make sure OpenMP is used in Cython and Eigen
    openmp_arg = "/openmp" if platform.startswith("win") else "-fopenmp"

    compile_args = [
        "--std=c++17",
        "-DNPY_NO_DEPRECATED_API=NPY_1_9_API_VERSION",
        openmp_arg,
    ]

    link_args = [openmp_arg]

    # Check for debug mode
    debug_mode = "--cython-gdb" in argv or os.environ.get(
        "BLASTER_DEBUG", ""
    ).lower() in ("1", "true", "yes")

    if debug_mode:
        print("Building in debug mode")
        debug_args = [
            "-O1",
            "-g",
            "-fno-omit-frame-pointer",
        ]
        # Only add sanitizers on platforms that support them
        if not platform.startswith("win"):
            debug_args.extend(
                [
                    "-fsanitize=address,undefined",
                ]
            )
        compile_args.extend(debug_args)
        link_args.extend(debug_args)
    else:
        print("Building in release mode")
        release_args = ["-O3", "-DEIGEN_NO_DEBUG"]
        # Only add -march=native on x86/x64 platforms
        import sysconfig

        machine = sysconfig.get_platform()
        if any(arch in machine for arch in ["x86", "amd64", "i686"]):
            release_args.append("-march=native")
        compile_args.extend(release_args)

    return compile_args, link_args


def main():
    """Main setup function."""
    print("Setting up BLASter with automatic Eigen3 management...")
    include_dirs = get_eigen_include_dirs()
    compile_args, link_args = get_compile_args()

    extensions = [
        Extension(
            name="blaster_core",
            sources=["core/blaster.pyx"],
            include_dirs=include_dirs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
            language="c++",
        )
    ]

    setup(
        ext_modules=cythonize(
            extensions,
            language_level="3",
            build_dir="build/cpp",
            compiler_directives={"embedsignature": True},
        ),
        zip_safe=False,
    )


if __name__ == "__main__":
    main()
