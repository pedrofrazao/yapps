import pandas as pd
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import re
import seaborn as sns
import numpy as np
import io

# Add a global mapping from gene names to descriptive labels
GENE_LABELS = {
    'gene1': 'move_change_direction_prob',
    'gene2': 'mate_minimal_age',
    'gene3': 'escape_from_distance_factor',
    'gene4': 'escape_from_count_factor',
    'gene5': 'see_length'
}

def load_csv(filepath):
    """
    Load a CSV with the specified format:
    1 - epoch of the simulation
    2 - class of the agent
    3 - energy of the agent
    4 - age of the agent
    5 - direction of the agent
    6 - chromosome encoding
    7+ - action info (ignored for basic analysis)
    
    First filters the file to include only lines matching the pattern.
    """
    # Filter the file content
    filtered_content = []
    regex_pattern = re.compile(r'^(.*\|[\d.]+,\w+)')
    
    with open(filepath, 'r') as file:
        line_count = 0
        filtered_count = 0
        
        for line in file:
            line_count += 1
            match = regex_pattern.match(line)
            if match:
                # Include only the content from the first capture group
                filtered_content.append(match.group(1))
            else:
                filtered_count += 1
    
    print(f"Filtered {filtered_count} lines out of {line_count} total lines")
    
    # Create a file-like object from filtered content
    filtered_data = io.StringIO('\n'.join(filtered_content))
    
    # Define column names
    columns = ['epoch', 'agent_class', 'energy', 'age', 'direction', 'chromosome', 'action_info']
    
    # Use pandas to read the filtered CSV
    df = pd.read_csv(filtered_data, header=None, names=columns, engine='python')
    
    # Convert columns to appropriate data types
    df['epoch'] = pd.to_numeric(df['epoch'])
    df['energy'] = pd.to_numeric(df['energy'])
    df['age'] = pd.to_numeric(df['age'])
    df['direction'] = pd.to_numeric(df['direction'])
    
    # Parse chromosome encoding
    df = parse_chromosomes(df)
    
    # Extract action type
    df['action_type'] = df['action_info'].apply(lambda x: x.split(' - ')[0] if isinstance(x, str) else None)
    
    return df

def load_multiple_csv(filepaths, required_epochs=None):
    """
    Load multiple CSV files and combine them into a single DataFrame.
    Filters out files that don't reach the required number of epochs.
    
    Parameters:
    -----------
    filepaths : list
        List of paths to CSV files
    required_epochs : int, optional
        Minimum number of epochs required to include a file
        
    Returns:
    --------
    DataFrame : Combined DataFrame from all valid files
    """
    all_dfs = []
    valid_files = 0
    skipped_files = 0
    
    for filepath in filepaths:
        print(f"Loading data from {filepath}...")
        try:
            df = load_csv(filepath)
            
            # Check if this file has enough epochs
            if required_epochs is not None:
                max_epoch = df['epoch'].max()
                if max_epoch < required_epochs - 1:  # -1 since epochs might be 0-indexed
                    print(f"  Skipping {filepath}: Only reached epoch {max_epoch}, required {required_epochs}")
                    skipped_files += 1
                    continue
            
            # Add a source column to track which file the data came from
            df['source_file'] = Path(filepath).name
            all_dfs.append(df)
            valid_files += 1
            
        except Exception as e:
            print(f"  Error loading {filepath}: {str(e)}")
            skipped_files += 1
    
    if not all_dfs:
        raise ValueError("No valid data files were loaded!")
    
    # Combine all DataFrames
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Successfully loaded {valid_files} files, skipped {skipped_files} files")
    print(f"Combined dataset has {len(combined_df)} records across {combined_df['epoch'].nunique()} epochs")
    
    return combined_df

def parse_chromosomes(df):
    """Parse chromosome encoding into separate columns"""
    # Extract the five chromosome values
    chromosome_data = df['chromosome'].str.split('|', expand=True)
    if len(chromosome_data.columns) >= 5:
        df['gene1'] = pd.to_numeric(chromosome_data[0], errors='coerce')
        df['gene2'] = pd.to_numeric(chromosome_data[1], errors='coerce')
        df['gene3'] = pd.to_numeric(chromosome_data[2], errors='coerce')
        df['gene4'] = pd.to_numeric(chromosome_data[3], errors='coerce')
        df['gene5'] = pd.to_numeric(chromosome_data[4], errors='coerce')
    
    return df

def analyze_by_epoch(df):
    """Generate statistics grouped by epoch"""
    epoch_stats = df.groupby('epoch').agg({
        'agent_class': 'count',
        'energy': ['mean', 'min', 'max', 'std'],
        'age': ['mean', 'max']
    })
    
    # Flatten multi-level column names
    epoch_stats.columns = ['_'.join(col).strip() for col in epoch_stats.columns.values]
    epoch_stats = epoch_stats.rename(columns={'agent_class_count': 'agent_count'})
    
    return epoch_stats

def plot_energy_stats(df, output_path=None):
    """Plot energy statistics by epoch"""
    energy_by_epoch = df.groupby('epoch')['energy'].agg(['mean', 'min', 'max'])
    
    plt.figure(figsize=(10, 6))
    plt.plot(energy_by_epoch.index, energy_by_epoch['mean'], 'b-', label='Mean Energy')
    plt.fill_between(
        energy_by_epoch.index, 
        energy_by_epoch['min'], 
        energy_by_epoch['max'], 
        alpha=0.2, 
        color='blue'
    )
    plt.title('Agent Energy by Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Energy')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def plot_age_stats(df, output_path=None):
    """Plot age statistics by epoch"""
    age_by_epoch = df.groupby('epoch')['age'].agg(['mean', 'min', 'max'])
    
    plt.figure(figsize=(10, 6))
    plt.plot(age_by_epoch.index, age_by_epoch['mean'], 'g-', label='Mean Age')
    plt.fill_between(
        age_by_epoch.index, 
        age_by_epoch['min'], 
        age_by_epoch['max'], 
        alpha=0.2, 
        color='green'
    )
    plt.title('Agent Age by Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Age')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def plot_agent_distribution(df, output_path=None):
    """Plot agent class distribution by epoch"""
    agent_counts = df.groupby(['epoch', 'agent_class']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(12, 6))
    for agent_class in agent_counts.columns:
        plt.plot(agent_counts.index, agent_counts[agent_class], marker='o', label=agent_class)
    
    plt.title('Agent Population by Class and Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Number of Agents')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def plot_action_distribution(df, output_path=None):
    """Plot action type distribution"""
    action_counts = df['action_type'].value_counts()
    
    plt.figure(figsize=(8, 6))
    action_counts.plot(kind='bar')
    plt.title('Agent Action Distribution')
    plt.xlabel('Action Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def analyze_chromosomes(df):
    """Analyze the prevalence and distribution of chromosome genes"""
    chrom_stats = {}
    
    # Calculate statistics for each chromosome
    for i in range(1, 6):  # Updated to process 5 genes
        col = f'gene{i}'
        if col in df.columns:
            chrom_stats[col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'most_common': df[col].value_counts().head(5).to_dict()
            }
    
    # Calculate correlations between chromosomes
    gene_cols = [f'gene{i}' for i in range(1, 6) if f'gene{i}' in df.columns]  # Updated to process 5 genes
    if len(gene_cols) > 1:
        chrom_stats['correlation'] = df[gene_cols].corr().to_dict()
    
    return chrom_stats

def plot_chromosome_distributions(df, output_dir=None):
    """Plot distributions of chromosome values"""
    gene_cols = [f'gene{i}' for i in range(1, 6) if f'gene{i}' in df.columns]  # Updated to process 5 genes
    
    if not gene_cols:
        print("No gene data available for plotting")
        return
    
    # Individual histograms for each chromosome
    plt.figure(figsize=(15, 10))  # Made figure larger to accommodate 5 plots
    for i, col in enumerate(gene_cols):
        plt.subplot(3, 2, i+1)  # Changed to 3x2 grid for 5 plots
        sns.histplot(df[col].dropna(), kde=True)
        # Use the descriptive label in the title
        plt.title(f'Distribution of {GENE_LABELS[col]}')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'gene_distributions.png')
        plt.close()
    else:
        plt.show()
    
    # Heatmap of chromosome value correlations
    if len(gene_cols) > 1:
        plt.figure(figsize=(12, 10))  # Made figure larger for 5 genes
        corr = df[gene_cols].corr()
        
        # Create a correlation matrix with descriptive labels
        sns.heatmap(
            corr, 
            annot=True, 
            cmap='coolwarm', 
            vmin=-1, 
            vmax=1,
            xticklabels=[GENE_LABELS[col] for col in gene_cols],
            yticklabels=[GENE_LABELS[col] for col in gene_cols]
        )
        plt.title('Gene Value Correlations')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(output_dir / 'gene_correlations.png')
            plt.close()
        else:
            plt.show()

def plot_chromosome_by_epoch(df, output_dir=None):
    """Plot how chromosome values change across epochs"""
    gene_cols = [f'gene{i}' for i in range(1, 6) if f'gene{i}' in df.columns]  # Updated to process 5 genes
    
    if not gene_cols:
        print("No gene data available for plotting")
        return
    
    plt.figure(figsize=(15, 10))  # Made figure larger to accommodate 5 plots
    
    for i, col in enumerate(gene_cols):
        # Calculate mean values by epoch
        gene_by_epoch = df.groupby('epoch')[col].mean()
        
        plt.subplot(3, 2, i+1)  # Changed to 3x2 grid for 5 plots
        plt.plot(gene_by_epoch.index, gene_by_epoch.values, marker='o')
        # Use the descriptive label in the title
        plt.title(f'{GENE_LABELS[col]} by Epoch')
        plt.xlabel('Epoch')
        plt.ylabel('Mean Value')
        plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'gene_by_epoch.png')
        plt.close()
    else:
        plt.show()

def plot_all_genes_by_epoch(df, output_dir=None):
    """Create a combined plot of all genes across epochs"""
    gene_cols = [f'gene{i}' for i in range(1, 6) if f'gene{i}' in df.columns]  # Updated to process 5 genes
    
    if not gene_cols:
        print("No gene data available for plotting")
        return
    
    plt.figure(figsize=(12, 6))
    
    for col in gene_cols:
        # Calculate mean values by epoch
        gene_by_epoch = df.groupby('epoch')[col].mean()
        # Plot each gene with a different color and use the descriptive label in the legend
        plt.plot(gene_by_epoch.index, gene_by_epoch.values, marker='o', label=GENE_LABELS[col])
    
    plt.title('Gene Values by Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Mean Value')
    plt.legend(loc='best')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'all_genes_by_epoch.png')
        plt.close()
    else:
        plt.show()

def plot_chromosome_frequency_by_epoch(df, output_dir=None, num_epoch_groups=10):
    """
    Plot frequency distribution of chromosome values by epoch as heatmaps
    Shows how the distribution of values changes over time
    
    Aggregates epochs into specified number of groups
    """
    gene_cols = [f'gene{i}' for i in range(1, 6) if f'gene{i}' in df.columns]  # Updated to process 5 genes
    
    if not gene_cols:
        print("No gene data available for plotting")
        return
    
    # Create a copy of the dataframe to avoid modifying the original
    plot_df = df.copy()
    
    # Determine epoch range and create bins
    min_epoch = plot_df['epoch'].min()
    max_epoch = plot_df['epoch'].max()
    epoch_range = max_epoch - min_epoch + 1
    
    # Create bin edges with approximately equal intervals
    bin_size = max(1, epoch_range / num_epoch_groups)
    bin_edges = [min_epoch + i * bin_size for i in range(num_epoch_groups+1)]
    
    # Apply binning to create epoch groups
    labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1]-1)}" for i in range(len(bin_edges)-1)]
    plot_df['epoch_group'] = pd.cut(plot_df['epoch'], bins=bin_edges, labels=labels, include_lowest=True)
    
    # Create a figure with enough subplots for 5 genes
    plt.figure(figsize=(18, 15))
    
    for i, col in enumerate(gene_cols):
        plt.subplot(3, 2, i+1)  # Changed to 3x2 grid for 5 plots
        
        # Create a crosstab to count frequencies by epoch group and gene value
        freq_table = pd.crosstab(plot_df['epoch_group'], plot_df[col])
        
        # Normalize by epoch group to get relative frequencies
        normalized_freq = freq_table.div(freq_table.sum(axis=1), axis=0)
        
        # Plot heatmap
        sns.heatmap(
            normalized_freq, 
            cmap='viridis', 
            cbar_kws={'label': 'Relative Frequency'}, 
            yticklabels=True
        )
        
        plt.title(f'Frequency of {GENE_LABELS[col]} Values by Epoch Group')
        plt.xlabel('Gene Value')
        plt.ylabel('Epoch Group')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'gene_frequency_by_epoch_group.png')
        plt.close()
    else:
        plt.show()

def plot_chromosome_value_counts(df, output_dir=None):
    """
    Plot stacked bar charts showing the count of each gene value by epoch
    """
    gene_cols = [f'gene{i}' for i in range(1, 6) if f'gene{i}' in df.columns]  # Updated to process 5 genes
    
    if not gene_cols:
        print("No gene data available for plotting")
        return
    
    # Create a figure with enough subplots for 5 genes
    fig = plt.figure(figsize=(18, 15))
    
    for i, col in enumerate(gene_cols):
        ax = fig.add_subplot(3, 2, i+1)  # Changed to 3x2 grid for 5 plots
        
        # Get unique epochs and gene values
        epochs = sorted(df['epoch'].unique())
        
        # Create a dictionary to store value counts by epoch
        counts_by_epoch = {}
        value_set = set()
        
        for epoch in epochs:
            epoch_data = df[df['epoch'] == epoch]
            value_counts = epoch_data[col].value_counts()
            counts_by_epoch[epoch] = value_counts
            value_set.update(value_counts.index)
        
        # Sort gene values and convert to list
        all_values = sorted(list(value_set))
        
        # Prepare data for stacked bar chart
        data = []
        for value in all_values:
            value_data = []
            for epoch in epochs:
                if value in counts_by_epoch[epoch]:
                    value_data.append(counts_by_epoch[epoch][value])
                else:
                    value_data.append(0)
            data.append(value_data)
        
        # Create stacked bar chart
        bottom = np.zeros(len(epochs))
        for j, value_data in enumerate(data):
            ax.bar(epochs, value_data, bottom=bottom, label=f'Value: {all_values[j]}')
            bottom += value_data
        
        ax.set_title(f'{GENE_LABELS[col]} Value Count by Epoch')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Count')
        ax.set_xticks(epochs)
        
        # Only show legend if there aren't too many values
        if len(all_values) <= 10:
            ax.legend(loc='upper right', fontsize='small')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'gene_value_counts.png')
        plt.close()
    else:
        plt.show()

def plot_simulation_completeness(df, expected_epochs, output_dir=None, num_groups=10):
    """
    Plot the percentage of simulations that ended at different epoch ranges
    
    Parameters:
    -----------
    df : DataFrame
        Combined DataFrame with simulation data
    expected_epochs : int
        The expected number of epochs each simulation should run
    output_dir : Path, optional
        Directory to save the output plot
    num_groups : int
        Number of epoch groups to divide the range into
    """
    if expected_epochs is None or 'source_file' not in df.columns:
        print("Skipping simulation completeness plot: Missing required data")
        return
    
    # Calculate the maximum epoch for each simulation
    max_epochs = df.groupby('source_file')['epoch'].max().reset_index()
    
    # Create bins for epoch ranges
    bin_size = expected_epochs / num_groups
    bin_edges = [i * bin_size for i in range(num_groups+1)]
    
    # Create labels for the bins
    labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1]-1)}" for i in range(len(bin_edges)-1)]
    
    # Assign each simulation to a bin based on its maximum epoch
    max_epochs['epoch_group'] = pd.cut(max_epochs['epoch'], 
                                       bins=bin_edges, 
                                       labels=labels, 
                                       include_lowest=True)
    
    # Count simulations in each bin
    completion_counts = max_epochs['epoch_group'].value_counts().sort_index()
    
    # Calculate percentages
    total_simulations = len(max_epochs)
    completion_percentages = completion_counts / total_simulations * 100
    
    # Create a bar chart
    plt.figure(figsize=(12, 6))
    completion_percentages.plot(kind='bar')
    plt.title('Percentage of Simulations by Maximum Epoch Reached')
    plt.xlabel('Epoch Range')
    plt.ylabel('Percentage of Simulations')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Add percentage labels on top of bars
    for i, v in enumerate(completion_percentages):
        plt.text(i, v + 1, f"{v:.1f}%", ha='center')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'simulation_completeness.png')
        plt.close()
    else:
        plt.show()

def save_chromosome_stats(stats, output_path):
    """Save chromosome statistics to CSV"""
    # Convert nested dictionary to a more CSV-friendly format
    rows = []
    
    for gene, values in stats.items():
        if gene == 'correlation':
            continue  # Handle correlations separately
        
        gene_label = GENE_LABELS.get(gene, gene)  # Use descriptive label if available
        
        for stat, value in values.items():
            if stat == 'most_common':
                for gene_val, count in value.items():
                    rows.append({
                        'gene': gene,
                        'gene_description': gene_label,
                        'statistic': f'most_common_{gene_val}',
                        'value': count
                    })
            else:
                rows.append({
                    'gene': gene,
                    'gene_description': gene_label,
                    'statistic': stat,
                    'value': value
                })
    
    # Convert to DataFrame and save
    stats_df = pd.DataFrame(rows)
    stats_df.to_csv(output_path, index=False)

def main():
    parser = argparse.ArgumentParser(description='Analyze simulation CSV data')
    parser.add_argument('csv_files', nargs='+', help='Path to one or more CSV files to analyze')
    parser.add_argument('--output-dir', '-o', help='Directory to save results', default='.')
    parser.add_argument('--num-epochs', '-e', type=int, help='Number of epochs each simulation ran', default=None)
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the data from all CSV files
    try:
        df = load_multiple_csv(args.csv_files, args.num_epochs)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return 1
    
    # Generate statistics
    epoch_stats = analyze_by_epoch(df)
    
    # Save statistics to CSV
    stats_file = output_dir / 'epoch_stats.csv'
    epoch_stats.to_csv(stats_file)
    print(f"Statistics saved to {stats_file}")
    
    # Generate plots
    print("Generating plots...")
    plot_energy_stats(df, output_dir / 'energy_stats.png')
    plot_age_stats(df, output_dir / 'age_stats.png')
    plot_agent_distribution(df, output_dir / 'agent_distribution.png')
    plot_action_distribution(df, output_dir / 'action_distribution.png')
    
    # Generate chromosome statistics and plots
    print("Analyzing gene data...")
    chrom_stats = analyze_chromosomes(df)
    
    # Save chromosome statistics
    gene_stats_file = output_dir / 'gene_stats.csv'
    save_chromosome_stats(chrom_stats, gene_stats_file)
    print(f"Gene statistics saved to {gene_stats_file}")
    
    # Generate chromosome plots
    print("Generating gene plots...")
    plot_chromosome_distributions(df, output_dir)
    plot_chromosome_by_epoch(df, output_dir)
    plot_all_genes_by_epoch(df, output_dir)
    
    # Add new frequency plots
    print("Generating gene frequency plots...")
    plot_chromosome_frequency_by_epoch(df, output_dir)
    plot_chromosome_value_counts(df, output_dir)
    
    # Add simulation completeness analysis
    if args.num_epochs:
        print("Analyzing simulation completeness...")
        plot_simulation_completeness(df, args.num_epochs, output_dir)
    
    print(f"Plots saved to {args.output_dir}")
    
    # Save processed data
    processed_file = output_dir / 'processed_data.csv'
    df.to_csv(processed_file, index=False)
    print(f"Processed data saved to {processed_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())
