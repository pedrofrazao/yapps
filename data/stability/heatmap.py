import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse
import os


# Parse command line arguments
parser = argparse.ArgumentParser(description='Create heatmap from CSV data')
parser.add_argument('-f', '--file', default='cr.csv',
                   help='Path to the input CSV file')
parser.add_argument('-t', '--title', default='heatmap',
                   help='plot title')
parser.add_argument('--has-f', action='store_true',
                   help='CSV has #F column for 3D heatmap')
args = parser.parse_args()

# Load the CSV file using the provided path
df = pd.read_csv(args.file)

# Get the name of the last column for the label
last_column = df.columns[-1]

if not args.has_f:
    # Original 2D heatmap logic
    # Extract unique values for #C and #R to create our grid
    c_values = sorted(df['#C'].unique())
    r_values = sorted(df['#R'].unique())

    # Create a pivot table for the heatmap
    pivot_data = df.pivot(index='#C', columns='#R', values=last_column)

    # Set up the plot
    plt.figure(figsize=(10, 8))

    # Create the heatmap with a logarithmic color scale
    heatmap = sns.heatmap(
        pivot_data, 
        annot=True, 
        fmt='.0f',
        cmap='viridis',
        norm=plt.cm.colors.LogNorm(vmin=1, vmax=pivot_data.max().max() + 1),
        cbar_kws={'label': f'{last_column} (log scale)'}
    )

    # Replace 0 values with custom text in the annotations
    for text, val in zip(heatmap.texts, pivot_data.values.flatten()):
        if pd.isna(val) or val == 0:
            text.set_text('0')
            text.set_color('white')  # Make zero values more visible

    # Set labels and title
    plt.title(args.title + ' - Heatmap of #R vs #C')
    plt.xlabel('#R')
    plt.ylabel('#C')

    # Adjust layout
    plt.tight_layout()

    # Save and display the figure
    plt.savefig(f'{os.path.splitext(args.file)[0]}_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()

else:
    # 3D heatmap logic (multiple 2D heatmaps, one for each #F value)
    # Extract unique values for #C, #R, and #F
    c_values = sorted(df['#C'].unique())
    r_values = sorted(df['#R'].unique())
    f_values = sorted(df['#F'].unique())
    
    # Determine grid size for subplot layout
    grid_size = int(np.ceil(np.sqrt(len(f_values))))
    
    # Create a figure with subplots
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(5*grid_size, 4*grid_size))
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]  # Handle single subplot case
    
    # Set a common color scale for all heatmaps
    vmax = df[last_column].max()
    
    for i, f_val in enumerate(f_values):
        if i >= len(axes):  # Safety check
            break
            
        # Filter data for this #F value
        df_f = df[df['#F'] == f_val]
        
        if len(df_f) == 0:
            continue
            
        # Create pivot table for this #F value
        pivot_data = df_f.pivot(index='#C', columns='#R', values=last_column)
        
        # Create heatmap in the corresponding subplot
        ax = axes[i]
        heatmap = sns.heatmap(
            pivot_data, 
            annot=True, 
            fmt='.0f',
            cmap='viridis',
            norm=plt.cm.colors.LogNorm(vmin=1, vmax=vmax + 1),
            cbar_kws={'label': f'{last_column} (log scale)'},
            ax=ax
        )
        
        # Replace 0 values with custom text in the annotations
        for text, val in zip(heatmap.texts, pivot_data.values.flatten()):
            if pd.isna(val) or val == 0:
                text.set_text('0')
                text.set_color('white')
        
        # Set subplot title and labels
        ax.set_title(f'#F = {f_val}')
        ax.set_xlabel('#R')
        ax.set_ylabel('#C')
    
    # Hide any unused subplots
    for j in range(i+1, len(axes)):
        axes[j].axis('off')
    
    # Set overall figure title
    fig.suptitle(f"{args.title} - Heatmaps of #R vs #C for different #F values", fontsize=16)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Make room for suptitle
    
    # Save and show figure
    plt.savefig(f'{os.path.splitext(args.file)[0]}_3d_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()