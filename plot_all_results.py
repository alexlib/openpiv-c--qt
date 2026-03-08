#!/usr/bin/env python3
"""Plot all PIV results from test2 dataset."""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_piv_data(filename):
    """Load PIV data from CSV-like output."""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('['):
                continue
            try:
                parts = line.split(',')
                x, y, u, v, sn = map(float, parts)
                data.append((x, y, u, v, sn))
            except (ValueError, IndexError):
                continue
    return np.array(data)

def plot_quiver(ax, data, title="", scale=80):
    """Create quiver plot on given axes."""
    x = data[:, 0]
    y = data[:, 1]
    u = data[:, 2]
    v = data[:, 3]
    sn = data[:, 4]
    speed = np.sqrt(u**2 + v**2)
    
    q = ax.quiver(x, y, u, v, speed, cmap='viridis', scale=scale, width=0.003)
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
    ax.set_title(f'{title}\nSpeed: {speed.min():.2f} - {speed.max():.2f} px')
    ax.set_aspect('equal')
    ax.invert_yaxis()
    return q

def main():
    test_dir = Path('examples/data/test2')
    piv_files = sorted(test_dir.glob('result_*.piv'))
    
    if not piv_files:
        print("No PIV result files found!")
        return
    
    print(f"Found {len(piv_files)} result files")
    
    # Create figure with subplots (2 rows x 3 cols)
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    all_speeds = []
    
    for idx, piv_file in enumerate(piv_files):
        data = load_piv_data(piv_file)
        print(f"Loaded {len(data)} vectors from {piv_file.name}")
        
        speed = np.sqrt(data[:, 2]**2 + data[:, 3]**2)
        all_speeds.extend(speed)
        
        plot_quiver(axes[idx], data, title=f"Frame Pair {idx}", scale=80)
    
    # Add common colorbar
    cbar = fig.colorbar(plt.cm.ScalarMappable(cmap='viridis'), 
                        ax=axes, orientation='vertical', 
                        shrink=0.8, label='Speed (pixels)')
    
    plt.suptitle('PIV Velocity Fields - Test2 Dataset (32x32, 50% overlap)', 
                 fontsize=14, y=1.02)
    plt.tight_layout()
    
    # Save figure
    output_file = test_dir / 'piv_results_all.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nSaved combined plot to {output_file}")
    
    # Print statistics
    all_speeds = np.array(all_speeds)
    print(f"\nOverall Statistics:")
    print(f"  Min speed: {all_speeds.min():.2f} px")
    print(f"  Max speed: {all_speeds.max():.2f} px")
    print(f"  Mean speed: {all_speeds.mean():.2f} px")
    print(f"  Std speed: {all_speeds.std():.2f} px")
    
    # Also create individual plots for each frame pair
    for idx, piv_file in enumerate(piv_files):
        data = load_piv_data(piv_file)
        speed = np.sqrt(data[:, 2]**2 + data[:, 3]**2)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        plot_quiver(ax, data, title=f"Frame Pair {idx}", scale=80)
        
        individual_file = test_dir / f'piv_result_{idx}.png'
        plt.savefig(individual_file, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved individual plot: {individual_file}")
    
    plt.show()

if __name__ == '__main__':
    main()
