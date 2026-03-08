#!/usr/bin/env python3
"""Plot PIV results from openpiv-c++ output."""

import sys
import numpy as np
import matplotlib.pyplot as plt

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

def plot_quiver(data, title="PIV Velocity Field", savefig=None):
    """Create quiver plot of velocity field."""
    x = data[:, 0]
    y = data[:, 1]
    u = data[:, 2]
    v = data[:, 3]
    sn = data[:, 4]
    speed_mag = np.sqrt(u**2 + v**2)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color by signal-to-noise ratio
    q = ax.quiver(x, y, u, v, sn, cmap='viridis', scale=50, width=0.003)
    
    # Add colorbar
    cbar = plt.colorbar(q, ax=ax, label='Signal-to-Noise')
    
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
    ax.set_title(f'{title}\nSpeed: {speed_mag.min():.2f} - {speed_mag.max():.2f} px')
    ax.set_aspect('equal')
    ax.invert_yaxis()  # Match image coordinates
    
    plt.tight_layout()
    
    if savefig:
        plt.savefig(savefig, dpi=150)
        print(f"Saved plot to {savefig}")
    else:
        plt.show()

def plot_scatter_sn(data, savefig=None):
    """Plot signal-to-noise distribution."""
    sn = data[:, 4]
    speed = np.sqrt(data[:, 2]**2 + data[:, 3]**2)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # SN histogram
    axes[0].hist(sn, bins=50, edgecolor='black')
    axes[0].set_xlabel('Signal-to-Noise Ratio')
    axes[0].set_ylabel('Count')
    axes[0].set_title(f'SN Distribution (mean={sn.mean():.2f}, std={sn.std():.2f})')
    axes[0].axvline(sn.mean(), color='r', linestyle='--', label='mean')
    axes[0].legend()
    
    # SN vs Speed scatter
    scatter = axes[1].scatter(data[:, 0], data[:, 1], c=sn, cmap='viridis', s=10)
    axes[1].set_xlabel('X (pixels)')
    axes[1].set_ylabel('Y (pixels)')
    axes[1].set_title('Vector positions colored by SN')
    axes[1].set_aspect('equal')
    axes[1].invert_yaxis()
    plt.colorbar(scatter, ax=axes[1], label='Signal-to-Noise')
    
    plt.tight_layout()
    
    if savefig:
        plt.savefig(savefig, dpi=150)
        print(f"Saved plot to {savefig}")
    else:
        plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python plot_piv.py <output.piv> [--quiver|--sn] [--save output.png]")
        sys.exit(1)
    
    piv_file = sys.argv[1]
    plot_type = '--quiver'
    savefig = None
    
    for arg in sys.argv[2:]:
        if arg in ('--quiver', '--sn'):
            plot_type = arg
        elif arg == '--save':
            idx = sys.argv.index(arg) + 1
            if idx < len(sys.argv):
                savefig = sys.argv[idx]
    
    data = load_piv_data(piv_file)
    print(f"Loaded {len(data)} vectors from {piv_file}")
    
    if plot_type == '--quiver':
        plot_quiver(data, savefig=savefig)
    else:
        plot_scatter_sn(data, savefig=savefig)
