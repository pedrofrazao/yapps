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
parser.add_argument('--dual-output', action='store_true',
                   help='CSV has two output columns to visualize')
parser.add_argument('--summary', choices=['mean', 'max', 'min', 'ratio'], default=None,
                   help='Summarize F values using mean, max, min or output ratio')
# Add filtering options
parser.add_argument('--filter-f', 
                   help='Comma-separated list of #F values to include (e.g., "2,4,8,16")')
parser.add_argument('--min-r', type=int,
                   help='Minimum value for #R to include')
parser.add_argument('--min-c', type=int,
                   help='Minimum value for #C to include')
parser.add_argument('--max-r', type=int,
                   help='Maximum value for #R to include')
parser.add_argument('--max-c', type=int,
                   help='Maximum value for #C to include')
args = parser.parse_args()

# Load the CSV file using the provided path
df = pd.read_csv(args.file)

# Apply filters if specified
if args.filter_f and '#F' in df.columns:
    filter_f_values = [int(f) for f in args.filter_f.split(',')]
    df = df[df['#F'].isin(filter_f_values)]

if args.min_r is not None:
    df = df[df['#R'] >= args.min_r]

if args.max_r is not None:
    df = df[df['#R'] <= args.max_r]

if args.min_c is not None:
    df = df[df['#C'] >= args.min_c]

if args.max_c is not None:
    df = df[df['#C'] <= args.max_c]

# For dual output, we need the last two columns
if args.dual_output:
    output_columns = df.columns[-2:]
else:
    # Get the name of the last column for the label
    output_columns = [df.columns[-1]]

# Normalize column names for file naming
def normalize_colname(name):
    return name.replace('#', '').replace(' ', '_')

# Calculate average values by dividing by number of runs
if 'run' in df.columns:
    for col in output_columns:
        df[f'{col}_avg'] = df[col] / df['run']
    # Use these new columns for visualization
    avg_output_columns = [f'{col}_avg' for col in output_columns]
else:
    # If there's no run column, use the original columns
    avg_output_columns = output_columns

if not args.has_f or not args.summary:
    # Original logic with either 2D heatmaps or full 3D visualization
    
    if not args.has_f:
        # Original 2D heatmap logic
        for i, output_col in enumerate(output_columns):
            avg_col = avg_output_columns[i]
            
            # Create a pivot table for the heatmap
            pivot_data = df.pivot(index='#C', columns='#R', values=avg_col)

            # Set up the plot
            plt.figure(figsize=(10, 8))

            # Create the heatmap with a logarithmic color scale
            heatmap = sns.heatmap(
                pivot_data, 
                annot=True, 
                fmt='.2f',  # Changed to 2 decimal places for averages
                cmap='viridis',
                norm=plt.cm.colors.LogNorm(vmin=0.1, vmax=pivot_data.max().max() + 0.1) if pivot_data.max().max() > 0 else None,
                cbar_kws={'label': f'{output_col} (average per run)'}
            )

            # Replace 0 values with custom text in the annotations
            for text, val in zip(heatmap.texts, pivot_data.values.flatten()):
                if pd.isna(val) or val == 0:
                    text.set_text('0')
                    text.set_color('white')  # Make zero values more visible

            # Set labels and title
            plt.title(f"{args.title} - Heatmap of #R vs #C ({output_col} average per run)")
            plt.xlabel('#R')
            plt.ylabel('#C')

            # Adjust layout
            plt.tight_layout()

            # Save and display the figure
            plt.savefig(f'{os.path.splitext(args.file)[0]}_{normalize_colname(output_col)}_avg_heatmap.png', 
                       dpi=300, bbox_inches='tight')
            plt.show()

    else:
        # Original 3D heatmap logic for each output column
        # Extract unique values for #C, #R, and #F
        c_values = sorted(df['#C'].unique())
        r_values = sorted(df['#R'].unique())
        f_values = sorted(df['#F'].unique())
        
        # Create plots for each output column
        for i, output_col in enumerate(output_columns):
            avg_col = avg_output_columns[i]
            
            # Determine grid size for subplot layout
            grid_size = int(np.ceil(np.sqrt(len(f_values))))
            
            # Create a figure with subplots
            fig, axes = plt.subplots(grid_size, grid_size, figsize=(5*grid_size, 4*grid_size))
            axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]  # Handle single subplot case
            
            # Set a common color scale for all heatmaps
            vmax = df[avg_col].max()
            
            for i, f_val in enumerate(f_values):
                if i >= len(axes):  # Safety check
                    break
                    
                # Filter data for this #F value
                df_f = df[df['#F'] == f_val]
                
                if len(df_f) == 0:
                    continue
                    
                # Create pivot table for this #F value
                pivot_data = df_f.pivot(index='#C', columns='#R', values=avg_col)
                
                # Create heatmap in the corresponding subplot
                ax = axes[i]
                heatmap = sns.heatmap(
                    pivot_data, 
                    annot=True, 
                    fmt='.2f',  # Changed to 2 decimal places for averages
                    cmap='viridis',
                    norm=plt.cm.colors.LogNorm(vmin=0.1, vmax=vmax + 0.1) if vmax > 0 else None,
                    cbar_kws={'label': f'{output_col} (average per run)'},
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
            fig.suptitle(f"{args.title} - Heatmaps of #R vs #C for different #F values ({output_col} average per run)", fontsize=16)
            
            # Adjust layout
            plt.tight_layout(rect=[0, 0, 1, 0.96])  # Make room for suptitle
            
            # Save and show figure
            plt.savefig(f'{os.path.splitext(args.file)[0]}_{normalize_colname(output_col)}_avg_3d_heatmap.png', 
                      dpi=300, bbox_inches='tight')
            plt.show()

else:
    # New summarized visualization approach
    # Extract unique values for parameters
    c_values = sorted(df['#C'].unique())
    r_values = sorted(df['#R'].unique())
    f_values = sorted(df['#F'].unique())
    
    # Create a summary visualization based on the selected method
    if args.summary == 'ratio' and args.dual_output:
        # For ratio summary, we need exactly two output columns
        if len(output_columns) != 2:
            print("Ratio summary requires exactly two output columns.")
            exit(1)
            
        # Create a new dataframe to hold the summarized data
        summary_df = pd.DataFrame()
        
        # For each combination of C and R, calculate the ratio across all F values
        for c in c_values:
            for r in r_values:
                subset = df[(df['#C'] == c) & (df['#R'] == r)]
                if not subset.empty:
                    # Calculate the ratio of the two output columns
                    ratios = subset[output_columns[0]] / subset[output_columns[1]]
                    avg_ratio = ratios.mean()
                    summary_df = summary_df.append({
                        '#C': c,
                        '#R': r,
                        'ratio': avg_ratio
                    }, ignore_index=True)
        
        # Create pivot table for the heatmap
        pivot_data = summary_df.pivot(index='#C', columns='#R', values='ratio')
        
        # Set up the plot
        plt.figure(figsize=(12, 10))
        
        # Create the heatmap
        heatmap = sns.heatmap(
            pivot_data,
            annot=True,
            fmt='.2f',
            cmap='RdYlGn',
            center=1.0,  # Center the color scale at ratio=1
            cbar_kws={'label': f'Ratio ({output_columns[0]} / {output_columns[1]})'}
        )
        
        # Set labels and title
        plt.title(f"{args.title} - Average Ratio of {output_columns[0]} to {output_columns[1]} across all #F values")
        plt.xlabel('#R')
        plt.ylabel('#C')
        
        # Save and display the figure
        plt.tight_layout()
        plt.savefig(f'{os.path.splitext(args.file)[0]}_ratio_summary.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    else:
        # For mean/max/min summary across F values
        # Set up the 2x2 grid for our summarized plots (or 1x2 for single output)
        n_cols = min(len(output_columns), 2)
        n_rows = (len(output_columns) + 1) // 2
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*7, n_rows*6))
        if n_rows * n_cols == 1:
            axes = np.array([axes])  # Make it indexable
        
        # Flatten axes for easier indexing
        axes = axes.flatten()
        
        for i, output_col in enumerate(output_columns):
            # Create a summary dataframe
            summary_df = pd.DataFrame()
            
            # For each combination of C and R, calculate the summary statistic across all F values
            for c in c_values:
                for r in r_values:
                    subset = df[(df['#C'] == c) & (df['#R'] == r)]
                    if not subset.empty:
                        if args.summary == 'mean':
                            summary_val = subset[output_col].mean()
                        elif args.summary == 'max':
                            summary_val = subset[output_col].max()
                        else:  # min
                            summary_val = subset[output_col].min()
                            
                        summary_df = summary_df.append({
                            '#C': c,
                            '#R': r,
                            'summary': summary_val
                        }, ignore_index=True)
            
            # Create pivot table for the heatmap
            pivot_data = summary_df.pivot(index='#C', columns='#R', values='summary')
            
            # Choose appropriate color map and normalization
            vmax = pivot_data.max().max()
            if vmax > 10:  # Use log scale for larger values
                norm = plt.cm.colors.LogNorm(vmin=1, vmax=vmax + 1)
                format_str = '.0f'
            else:
                norm = None
                format_str = '.2f'
            
            # Create the heatmap in the corresponding subplot
            ax = axes[i]
            heatmap = sns.heatmap(
                pivot_data,
                annot=True,
                fmt=format_str,
                cmap='viridis',
                norm=norm,
                cbar_kws={'label': f'{output_col} ({args.summary})'},
                ax=ax
            )
            
            # Replace 0 values with custom text in the annotations
            for text, val in zip(heatmap.texts, pivot_data.values.flatten()):
                if pd.isna(val) or val == 0:
                    text.set_text('0')
                    text.set_color('white')
            
            # Set subplot title and labels
            ax.set_title(f'{output_col} - {args.summary.capitalize()} across all #F values')
            ax.set_xlabel('#R')
            ax.set_ylabel('#C')
        
        # Hide any unused subplots
        for j in range(len(output_columns), len(axes)):
            axes[j].axis('off')
        
        # Set overall figure title
        fig.suptitle(f"{args.title} - Summary: {args.summary.capitalize()} across all #F values", fontsize=16)
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # Make room for suptitle
        
        # Save and show figure
        plt.savefig(f'{os.path.splitext(args.file)[0]}_{args.summary}_summary.png', dpi=300, bbox_inches='tight')
        plt.show()

    # Add a 3D scatter plot for deeper analysis (shows all dimensions and both outputs)
    if args.dual_output and len(output_columns) == 2:
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create scatter plot with color representing the first output, size representing the second
        scatter = ax.scatter(
            df['#R'], 
            df['#C'], 
            df['#F'],
            c=df[output_columns[0]], 
            s=df[output_columns[1]] / df[output_columns[1]].max() * 200,  # Scale size
            cmap='viridis',
            alpha=0.7
        )
        
        # Add colorbar for the first output
        cbar = plt.colorbar(scatter)
        cbar.set_label(output_columns[0])
        
        # Add size legend for the second output
        sizes = [df[output_columns[1]].min(), df[output_columns[1]].median(), df[output_columns[1]].max()]
        size_legend = [plt.scatter([], [], s=size / df[output_columns[1]].max() * 200, 
                                  c='gray', alpha=0.7) for size in sizes]
        plt.legend(size_legend, [f'{int(size)}' for size in sizes], 
                  title=output_columns[1], loc='upper left', bbox_to_anchor=(1, 0.8))
        
        # Set labels and title
        ax.set_xlabel('#R')
        ax.set_ylabel('#C')
        ax.set_zlabel('#F')
        plt.title(f"{args.title} - 3D Parameter Space with Dual Outputs")
        
        # Adjust layout
        plt.tight_layout()
        
        # Save and display the figure
        plt.savefig(f'{os.path.splitext(args.file)[0]}_3d_scatter.png', dpi=300, bbox_inches='tight')
        plt.show()