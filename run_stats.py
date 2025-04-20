import pandas as pd
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import re
import seaborn as sns
import numpy as np

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
    """
    # Define column names
    columns = ['epoch', 'agent_class', 'energy', 'age', 'direction', 'chromosome', 'action_info']
    
    # Use pandas to read the CSV
    df = pd.read_csv(filepath, header=None, names=columns, engine='python')
    
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

def parse_chromosomes(df):
    """Parse chromosome encoding into separate columns"""
    # Extract the four chromosome values
    chromosome_data = df['chromosome'].str.split('|', expand=True)
    if len(chromosome_data.columns) >= 4:
        df['chrom1'] = pd.to_numeric(chromosome_data[0], errors='coerce')
        df['chrom2'] = pd.to_numeric(chromosome_data[1], errors='coerce')
        df['chrom3'] = pd.to_numeric(chromosome_data[2], errors='coerce')
        df['chrom4'] = pd.to_numeric(chromosome_data[3], errors='coerce')
    
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
    for i in range(1, 5):
        col = f'chrom{i}'
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
    chrom_cols = [f'chrom{i}' for i in range(1, 5) if f'chrom{i}' in df.columns]
    if len(chrom_cols) > 1:
        chrom_stats['correlation'] = df[chrom_cols].corr().to_dict()
    
    return chrom_stats

def plot_chromosome_distributions(df, output_dir=None):
    """Plot distributions of chromosome values"""
    chrom_cols = [f'chrom{i}' for i in range(1, 5) if f'chrom{i}' in df.columns]
    
    if not chrom_cols:
        print("No chromosome data available for plotting")
        return
    
    # Individual histograms for each chromosome
    plt.figure(figsize=(12, 8))
    for i, col in enumerate(chrom_cols):
        plt.subplot(2, 2, i+1)
        sns.histplot(df[col].dropna(), kde=True)
        plt.title(f'Distribution of {col}')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'chromosome_distributions.png')
        plt.close()
    else:
        plt.show()
    
    # Heatmap of chromosome value correlations
    if len(chrom_cols) > 1:
        plt.figure(figsize=(8, 6))
        corr = df[chrom_cols].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('Chromosome Value Correlations')
        
        if output_dir:
            plt.savefig(output_dir / 'chromosome_correlations.png')
            plt.close()
        else:
            plt.show()

def plot_chromosome_by_epoch(df, output_dir=None):
    """Plot how chromosome values change across epochs"""
    chrom_cols = [f'chrom{i}' for i in range(1, 5) if f'chrom{i}' in df.columns]
    
    if not chrom_cols:
        print("No chromosome data available for plotting")
        return
    
    plt.figure(figsize=(12, 8))
    
    for i, col in enumerate(chrom_cols):
        # Calculate mean values by epoch
        chrom_by_epoch = df.groupby('epoch')[col].mean()
        
        plt.subplot(2, 2, i+1)
        plt.plot(chrom_by_epoch.index, chrom_by_epoch.values, marker='o')
        plt.title(f'Mean {col} Value by Epoch')
        plt.xlabel('Epoch')
        plt.ylabel('Mean Value')
        plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'chromosome_by_epoch.png')
        plt.close()
    else:
        plt.show()

def save_chromosome_stats(stats, output_path):
    """Save chromosome statistics to CSV"""
    # Convert nested dictionary to a more CSV-friendly format
    rows = []
    
    for chrom, values in stats.items():
        if chrom == 'correlation':
            continue  # Handle correlations separately
        
        for stat, value in values.items():
            if stat == 'most_common':
                for gene_val, count in value.items():
                    rows.append({
                        'chromosome': chrom,
                        'statistic': f'most_common_{gene_val}',
                        'value': count
                    })
            else:
                rows.append({
                    'chromosome': chrom,
                    'statistic': stat,
                    'value': value
                })
    
    # Convert to DataFrame and save
    stats_df = pd.DataFrame(rows)
    stats_df.to_csv(output_path, index=False)

def main():
    parser = argparse.ArgumentParser(description='Analyze simulation CSV data')
    parser.add_argument('csv_file', help='Path to the CSV file to analyze')
    parser.add_argument('--output-dir', '-o', help='Directory to save results', default='.')
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the data
    print(f"Loading data from {args.csv_file}...")
    df = load_csv(args.csv_file)
    print(f"Loaded {len(df)} records across {df['epoch'].nunique()} epochs")
    
    # Generate statistics
    epoch_stats = analyze_by_epoch(df)
    
    # Save statistics to CSV
    stats_file = output_dir / 'epoch_stats.csv'
    epoch_stats.to_csv(stats_file)
    print(f"Statistics saved to {stats_file}")
    
    # Generate plots
    print("Generating plots...")
    plot_energy_stats(df, output_dir / 'energy_stats.png')
    plot_age_stats(df, output_dir / 'age_stats.png')  # New age stats plot
    plot_agent_distribution(df, output_dir / 'agent_distribution.png')
    plot_action_distribution(df, output_dir / 'action_distribution.png')
    
    # Generate chromosome statistics and plots
    print("Analyzing chromosome data...")
    chrom_stats = analyze_chromosomes(df)
    
    # Save chromosome statistics
    chrom_stats_file = output_dir / 'chromosome_stats.csv'
    save_chromosome_stats(chrom_stats, chrom_stats_file)
    print(f"Chromosome statistics saved to {chrom_stats_file}")
    
    # Generate chromosome plots
    print("Generating chromosome plots...")
    plot_chromosome_distributions(df, output_dir)
    plot_chromosome_by_epoch(df, output_dir)
    
    print(f"Plots saved to {args.output_dir}")
    
    # Save processed data
    processed_file = output_dir / 'processed_data.csv'
    df.to_csv(processed_file, index=False)
    print(f"Processed data saved to {processed_file}")

if __name__ == "__main__":
    main()
