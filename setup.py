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
import subprocess
import sys
from pathlib import Path

import pybind11
from setuptools import Extension, setup

ROOT_DIR = Path(__file__).parent.resolve()


def pkg_config(library, option):
    """Run pkg-config and return the result."""
    try:
        result = subprocess.check_output(
            ["pkg-config", option, library],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return result.split() if result else []
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_tiff_config():
    """Get libtiff compile/link flags via pkg-config or environment."""
    include_dirs = []
    library_dirs = []
    libraries = ["tiff"]

    # Try pkg-config first
    cflags = pkg_config("libtiff-4", "--cflags")
    libs = pkg_config("libtiff-4", "--libs")

    for flag in cflags:
        if flag.startswith("-I"):
            include_dirs.append(flag[2:])

    for flag in libs:
        if flag.startswith("-L"):
            library_dirs.append(flag[2:])
        elif flag.startswith("-l"):
            pass  # already have 'tiff' in libraries

    # Fallback: check environment variables (used by CI)
    tiff_include = os.environ.get("TIFF_INCLUDE_DIR") or os.environ.get(
        "LIBTIFF_INCLUDE_DIR"
    )
    tiff_library = os.environ.get("TIFF_LIBRARY") or os.environ.get("LIBTIFF_LIBRARY")

    if tiff_include and Path(tiff_include).is_dir():
        include_dirs.append(tiff_include)

    if tiff_library:
        lib_path = Path(tiff_library).parent
        if lib_path.is_dir():
            library_dirs.append(str(lib_path))

    # Windows: try vcpkg installed directory
    if sys.platform == "win32":
        vcpkg_root = os.environ.get("VCPKG_INSTALLED_DIR")
        if not vcpkg_root:
            # Try common vcpkg locations
            for candidate in [
                Path("C:/vcpkg/installed/x64-windows"),
                Path(os.environ.get("GITHUB_WORKSPACE", ""))
                / "vcpkg_installed"
                / "x64-windows",
            ]:
                if candidate.is_dir():
                    vcpkg_root = str(candidate)
                    break

        if vcpkg_root:
            vcpkg_inc = Path(vcpkg_root) / "include"
            vcpkg_lib = Path(vcpkg_root) / "lib"
            if vcpkg_inc.is_dir() and str(vcpkg_inc) not in include_dirs:
                include_dirs.append(str(vcpkg_inc))
            if vcpkg_lib.is_dir() and str(vcpkg_lib) not in library_dirs:
                library_dirs.append(str(vcpkg_lib))

    return include_dirs, library_dirs, libraries


def get_extensions():
    """Build extension module with all C++ sources compiled in."""
    # C++ source files for the openpiv core library
    # Only include sources actually used by piv_bindings.cpp
    openpiv_sources = [
        "openpiv/core/size.cpp",
        "openpiv/core/rect.cpp",
        "openpiv/core/util.cpp",
        "openpiv/loaders/image_loader.cpp",
        "openpiv/loaders/pnm_image_loader.cpp",
        "openpiv/loaders/tiff_image_loader.cpp",
        "external/libtiff/4.0.10/tif_stream.cxx",
    ]

    # pybind11 binding source
    binding_sources = ["piv_bindings.cpp"]

    all_sources = openpiv_sources + binding_sources

    # Include directories
    include_dirs = [
        str(ROOT_DIR),  # for openpiv/ prefix includes
        str(ROOT_DIR / "openpiv"),  # for core/ rect/ etc. includes
        str(ROOT_DIR / "external" / "pocketfft"),
        str(ROOT_DIR / "external" / "threading"),
        str(ROOT_DIR / "external" / "libtiff" / "4.0.10"),
        pybind11.get_include(),
    ]

    # Get libtiff configuration
    tiff_inc, tiff_lib_dirs, tiff_libs = get_tiff_config()
    include_dirs.extend(tiff_inc)

    # Compiler flags
    if sys.platform == "win32":
        extra_compile_args = ["/O2", "/std:c++17", "/D_USE_MATH_DEFINES"]
        extra_link_args = []
    else:
        extra_compile_args = [
            "-O3",
            "-std=c++17",
            "-fvisibility=hidden",
            "-ffast-math",
            "-Wno-unknown-pragmas",
        ]
        extra_link_args = []
        if sys.platform == "darwin":
            extra_link_args.append("-Wl,-rpath,@loader_path")
        else:
            extra_link_args.append("-Wl,-rpath,$ORIGIN")

    return [
        Extension(
            "openpiv_cpp_pkg.openpiv_cpp",
            sources=all_sources,
            include_dirs=include_dirs,
            library_dirs=tiff_lib_dirs,
            libraries=tiff_libs,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            language="c++",
        ),
    ]


readme_path = ROOT_DIR / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    ext_modules=get_extensions(),
    long_description=long_description,
    long_description_content_type="text/markdown",
)
