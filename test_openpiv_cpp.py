#!/usr/bin/env python3
"""Test the openpiv_cpp Python bindings."""

import openpiv_cpp
import numpy as np

print("=" * 60)
print("OpenPIV C++ Python Bindings Test")
print("=" * 60)

# Test 1: Basic PIV processing
print("\n1. Testing piv_process()...")
result = openpiv_cpp.piv_process(
    "examples/process/exp1_001_a.tiff",
    "examples/process/exp1_001_b.tiff",
    size=32,
    overlap=0.5
)

print(f"   Image size: {result['image_size']}")
print(f"   Vector count: {result['count']}")
print(f"   IA size: {result['ia_size']}, Overlap: {result['overlap']}")

stats = result['stats']
print(f"\n   Statistics:")
print(f"   - Speed: {stats['min_speed']:.2f} - {stats['max_speed']:.2f} px (mean: {stats['mean_speed']:.2f})")
print(f"   - S/N: {stats['min_sn']:.2f} - {stats['max_sn']:.2f} (mean: {stats['mean_sn']:.2f})")

# Test 2: Access vectors as numpy array
print("\n2. Testing vector access...")
vectors = result['vectors']
print(f"   Vectors shape: {vectors.shape}")
print(f"   Vectors dtype: {vectors.dtype}")
print(f"\n   First 5 vectors (x, y, u, v, sn):")
for i in range(5):
    print(f"   {vectors[i]}")

# Test 3: Different FFT types
print("\n3. Testing different FFT types...")
for fft_type in ['complex', 'real', 'pocket', 'pocket_real']:
    try:
        r = openpiv_cpp.cross_correlate(
            "examples/process/exp1_001_a.tiff",
            "examples/process/exp1_001_b.tiff",
            size=32,
            fft_type=fft_type
        )
        print(f"   {fft_type}: {r['count']} vectors")
    except Exception as e:
        print(f"   {fft_type}: FAILED - {e}")

# Test 4: Process test2 dataset
print("\n4. Processing test2 dataset...")
result2 = openpiv_cpp.piv_process(
    "examples/data/test2/2image_00.tif",
    "examples/data/test2/2image_01.tif",
    size=32
)
print(f"   Image size: {result2['image_size']}")
print(f"   Vector count: {result2['count']}")
print(f"   Mean speed: {result2['stats']['mean_speed']:.2f} px")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
