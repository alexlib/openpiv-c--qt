"""
Setup script for OpenPIV C++ Python bindings.

Build wheels with:
    pip install build cibuildwheel
    python -m cibuildwheel --output-dir wheelhouse

Or build locally with:
    pip install build
    python -m build --wheel
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pybind11


def get_build_requirements():
    """Check if we need to build the C++ library."""
    build_dir = Path(__file__).parent / "builddir" / "openpiv"
    lib_file = build_dir / "libopenpiv.so"
    return not lib_file.exists()


def build_cpp_library():
    """Build the C++ library using CMake."""
    print("Building C++ library with CMake...")

    # Source and build directories
    src_dir = Path(__file__).parent
    build_dir = src_dir / "builddir"

    # Ensure build directory exists
    build_dir.mkdir(parents=True, exist_ok=True)

    # Configure with CMake
    subprocess.check_call(
        ["cmake", "-S", str(src_dir), "-B", str(build_dir)]
    )

    # Build with CMake
    subprocess.check_call(
        ["cmake", "--build", str(build_dir), "--config", "Release"]
    )
    print("C++ library built successfully!")


class CustomBuildExt(build_ext):
    """Custom build extension that builds C++ library first."""
    
    def run(self):
        # Build C++ library if needed
        build_dir = Path(__file__).parent / "builddir" / "openpiv"
        lib_file = build_dir / "libopenpiv.so"
        
        if not lib_file.exists():
            try:
                build_cpp_library()
            except Exception as e:
                print(f"Warning: Could not build C++ library: {e}")
                print("Continuing without C++ library...")
        
        super().run()
    
    def build_extension(self, ext):
        # Get the extension output directory
        extdir = Path(self.get_ext_fullpath(ext.name)).parent
        extdir.mkdir(parents=True, exist_ok=True)
        
        # Build using setup.py approach with pre-built library
        build_dir = Path(__file__).parent / "builddir" / "openpiv"
        
        # Compiler flags
        if getattr(self, "compiler", None) is not None and self.compiler.compiler_type == "msvc":
            extra_compile_args = ["/O2", "/std:c++17"]
        else:
            extra_compile_args = ["-O3", "-std=c++17", "-fvisibility=hidden"]
        extra_link_args = []
        
        libraries = []
        library_dirs = []
        runtime_library_dirs = []
        
        # Link against pre-built library if available
        if build_dir.exists():
            lib_file = build_dir / "libopenpiv.so"
            if lib_file.exists():
                libraries = ["openpiv"]
                library_dirs = [str(build_dir)]
                if sys.platform.startswith("linux"):
                    runtime_library_dirs = [str(build_dir)]
                    extra_link_args.append("-Wl,-rpath," + str(build_dir))
        
        # Update extension
        ext.include_dirs.append(pybind11.get_include())
        ext.extra_compile_args = extra_compile_args
        ext.extra_link_args = extra_link_args
        ext.libraries = libraries
        ext.library_dirs = library_dirs
        ext.runtime_library_dirs = runtime_library_dirs
        
        # Build the extension
        super().build_extension(ext)


def get_extensions():
    """Get extension modules."""
    ext_modules = [
        Extension(
            "openpiv_cpp_pkg.openpiv_cpp",
            ["piv_bindings.cpp"],
            include_dirs=[
                "openpiv",
                "external/pocketfft",
                "subprojects/fmt-9.1.0/include",
            ],
            language="c++",
        ),
    ]
    return ext_modules


# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")


setup(
    ext_modules=get_extensions(),
    cmdclass={"build_ext": CustomBuildExt},
    long_description=long_description,
    long_description_content_type="text/markdown",
)
