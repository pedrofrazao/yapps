#!/usr/bin/env python3
# filepath: /home/pedro/develop/gui_tests/plot_simulation.py
import argparse
import yaml
import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any
import seaborn as sns
import pandas as pd
from pathlib import Path

# Import the YMLArenaLoader class
from ppSlib.yml_loader import YMLArenaLoader  # Adjust this import path as needed

args = None

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Generate plots from simulation CSV data")
    parser.add_argument("--file", required=False, help="YAML file that defines the simulation")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--summary-csv", help="Path to a precomputed summary_stats CSV file (alternative to CSV files)")
    parser.add_argument("csv_files", nargs="*", help="List of CSV files to load")
    return parser.parse_args()

def load_yaml_config(yaml_path):
    """Load the YAML configuration file using YMLArenaLoader"""
    loader = YMLArenaLoader()
    return loader.load_yml_config(yaml_path)

def extract_data_from_csv(csv_file, arena_config):
    """Extract data from CSV file by parsing its specific format, using ArenaConfig for gene naming"""
    # Initialize data structures
    epoch_data = {}
    allele_data = {}
    
    # Get gene mappings from config
    agent_genes = arena_config.get_agent_genes()
    
    # Process the file line by line
    with open(csv_file, 'r') as f:
        # Find where the actual data starts (skip the grid visualization)
        data_started = False
        for line in f:
            # Check if this line matches the pattern of actual data
            if not data_started and re.match(r'\d+,\w+,\d+,\d+,\d+,.*', line):
                data_started = True
            if not data_started:
                continue

            parts = line.strip().split(',')
            if len(parts) >= 6:
                try:
                    epoch = int(parts[0])
                    agent_type = parts[1]
                    energy = int(parts[2])
                    age = int(parts[3])
                    
                    # Initialize data structures if needed
                    if epoch not in epoch_data:
                        epoch_data[epoch] = defaultdict(list)
                    if epoch not in allele_data:
                        allele_data[epoch] = {}
                    if agent_type not in allele_data[epoch]:
                        allele_data[epoch][agent_type] = defaultdict(lambda: defaultdict(int))
                    
                    # Add agent data
                    epoch_data[epoch][agent_type].append({
                        "energy": energy,
                        "age": age
                    })
                    
                    # Parse allele information
                    try:
                        allele_info = parts[5]
                        allele_parts = allele_info.split('|')
                        
                        # Verify if allele_parts has the expected format
                        if allele_parts and len(allele_parts) <= len(agent_genes.get(agent_type, [])):
                            # Add allele data
                            i = 0
                            for v in allele_parts:
                                if i < len(agent_genes.get(agent_type, [])):
                                    gene_name = agent_genes[agent_type][i]
                                    if gene_name not in allele_data[epoch][agent_type]:
                                        allele_data[epoch][agent_type][gene_name] = defaultdict(int)
                                    allele_data[epoch][agent_type][gene_name][v] += 1
                                    i += 1
                    except (IndexError, KeyError):
                        # Ignore if allele info is missing or not in the correct format
                        pass
                        
                except Exception as e:
                    print(f"Error processing line: {line.strip()} - {e}")
    
    return epoch_data, allele_data

def analyze_data(csv_files, arena_config):
    """Analyze data from multiple CSV files using arena configuration"""
    all_agent_data = {}
    all_allele_data = {}
    max_epoch = 0
    
    id = 0
    for csv_file in csv_files:
        id += 1
        agent_data, allele_data = extract_data_from_csv(csv_file, arena_config)
        
        all_agent_data[id] = agent_data
        all_allele_data[id] = allele_data

    max_epoch = max([max(epoch_data.keys()) for epoch_data in all_agent_data.values()])

    # Calculate summary statistics
    summary_stats = []
    
    for i in range(id + 1):
        if i not in all_agent_data:
            continue
        for epoch in range(1,max_epoch + 1):
            if epoch not in all_agent_data[i]:
                continue
            agent_data = all_agent_data[i].get(epoch, {})
            for agent_type, agents in agent_data.items():
                if not agents:
                    continue
                
                row = {
                    "run": i,
                    "epoch": epoch,
                    "agent_type": agent_type,
                    "count": len(agents),
                    "avg_energy": sum(a["energy"] for a in agents) / len(agents),
                    "avg_age": sum(a["age"] for a in agents) / len(agents),
                }
                
                for gene, value in all_allele_data[i][epoch][agent_type].items():
                    for allele, count in value.items():
                        k = f"{gene}_{allele}"
                        if k not in row:
                            row[k] = 0
                        row[k] += count                
                
                summary_stats.append(row)
    
    # Convert summary_stats to a pandas DataFrame
    summary_df = pd.DataFrame(summary_stats)
    if ( args.verbose ):
        print(summary_df.head().transpose())
    return summary_df, max_epoch


def create_plots(summary_stats, epochs, output_dir="plots"):
    """Generate plots based on the summary statistics"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    agent_types = sorted(summary_stats['agent_type'].unique())
    

    plot_agent_count_boxplot_by_bins(summary_stats, agent_types, epochs, output_dir)    
    plot_agent_energy_boxplot_by_bins(summary_stats, agent_types, epochs, output_dir)
    plot_agent_age_boxplot_by_bins(summary_stats, agent_types, epochs, output_dir)

    plot_gene_heatmaps(summary_stats, agent_types, epochs, output_dir)


def plot_agent_count_by_bins(summary_stats, agent_types, epochs, output_dir):
    """Create a plot showing agent count by epoch bins and agent type"""
    if not epochs:
        return
    
    min_epoch = max(1, min(epochs))
    max_epoch = max(epochs)
    bin_range = max_epoch - min_epoch + 1
    bin_width = bin_range / 10
    
    bins = []
    bin_labels = []
    
    for i in range(10):
        bin_start = min_epoch + int(i * bin_width)
        bin_end = min_epoch + int((i + 1) * bin_width) - 1
        if i == 9:
            bin_end = max_epoch
        
        bins.append((bin_start, bin_end))
        bin_labels.append(f"{bin_start}-{bin_end}")
    
    bin_averages = {agent_type: [] for agent_type in agent_types}
    
    for bin_start, bin_end in bins:
        bin_epochs = [e for e in epochs if bin_start <= e <= bin_end]
        
        for agent_type in agent_types:
            all_counts = []
            for epoch in bin_epochs:
                if agent_type in summary_stats[epoch]:
                    all_counts.append(summary_stats[epoch][agent_type].get("count", 0))
            
            if all_counts:
                bin_averages[agent_type].append(sum(all_counts) / len(all_counts))
            else:
                bin_averages[agent_type].append(0)
    
    plt.figure(figsize=(12, 8))
    x = range(len(bin_labels))
    
    for agent_type in agent_types:
        plt.plot(x, bin_averages[agent_type], marker='o', linewidth=2, label=agent_type)
    
    plt.xlabel('Epoch Bins')
    plt.ylabel('Average Agent Count')
    plt.title('Average Agent Count by Epoch Bins')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'agent_count_by_bins.png'))
    plt.close()

def plot_age_by_bins(summary_stats, agent_types, epochs, output_dir):
    """Create a plot showing average age by epoch bins and agent type"""
    if not epochs:
        return
    
    min_epoch = max(1, min(epochs))
    max_epoch = max(epochs)
    bin_range = max_epoch - min_epoch + 1
    bin_width = bin_range / 10
    
    bins = []
    bin_labels = []
    
    for i in range(10):
        bin_start = min_epoch + int(i * bin_width)
        bin_end = min_epoch + int((i + 1) * bin_width) - 1
        if i == 9:
            bin_end = max_epoch
        
        bins.append((bin_start, bin_end))
        bin_labels.append(f"{bin_start}-{bin_end}")
    
    bin_averages = {agent_type: [] for agent_type in agent_types}
    
    for bin_start, bin_end in bins:
        bin_epochs = [e for e in epochs if bin_start <= e <= bin_end]
        
        for agent_type in agent_types:
            all_ages = []
            for epoch in bin_epochs:
                if agent_type in summary_stats[epoch] and summary_stats[epoch][agent_type].get("count", 0) > 0:
                    all_ages.append(summary_stats[epoch][agent_type]["avg_age"])
            
            if all_ages:
                bin_averages[agent_type].append(sum(all_ages) / len(all_ages))
            else:
                bin_averages[agent_type].append(0)
    
    plt.figure(figsize=(12, 8))
    x = range(len(bin_labels))
    
    for agent_type in agent_types:
        plt.plot(x, bin_averages[agent_type], marker='o', linewidth=2, label=agent_type)
    
    plt.xlabel('Epoch Bins')
    plt.ylabel('Average Age')
    plt.title('Average Agent Age by Epoch Bins')
    plt.xticks(x, bin_labels, rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'avg_age_by_bins.png'))
    plt.close()

def plot_energy_by_bins(summary_stats, agent_types, epochs, output_dir):
    """Create a plot showing average energy by epoch bins and agent type"""
    if not epochs:
        return
    
    min_epoch = max(1, min(epochs))
    max_epoch = max(epochs)
    bin_range = max_epoch - min_epoch + 1
    bin_width = bin_range / 10
    
    bins = []
    bin_labels = []
    
    for i in range(10):
        bin_start = min_epoch + int(i * bin_width)
        bin_end = min_epoch + int((i + 1) * bin_width) - 1
        if i == 9:
            bin_end = max_epoch
        
        bins.append((bin_start, bin_end))
        bin_labels.append(f"{bin_start}-{bin_end}")
    
    bin_averages = {agent_type: [] for agent_type in agent_types}
    
    for bin_start, bin_end in bins:
        bin_epochs = [e for e in epochs if bin_start <= e <= bin_end]
        
        for agent_type in agent_types:
            all_energies = []
            for epoch in bin_epochs:
                if agent_type in summary_stats[epoch] and summary_stats[epoch][agent_type].get("count", 0) > 0:
                    all_energies.append(summary_stats[epoch][agent_type]["avg_energy"])
            
            if all_energies:
                bin_averages[agent_type].append(sum(all_energies) / len(all_energies))
            else:
                bin_averages[agent_type].append(0)
    
    plt.figure(figsize=(12, 8))
    x = range(len(bin_labels))
    
    for agent_type in agent_types:
        plt.plot(x, bin_averages[agent_type], marker='o', linewidth=2, label=agent_type)
    
    plt.xlabel('Epoch Bins')
    plt.ylabel('Average Energy')
    plt.title('Average Agent Energy by Epoch Bins')
    plt.xticks(x, bin_labels, rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'avg_energy_by_bins.png'))
    plt.close()

def plot_gene_heatmaps(summary_stats, agent_types, epochs, output_dir):
    """Create heatmaps showing the deviation from uniform allele frequency by epoch bins for each agent type using the summary_stats DataFrame"""
    if not epochs:
        return

    min_epoch = 1
    max_epoch = epochs
    bin_edges = np.linspace(min_epoch, max_epoch, 11)
    bin_labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(bin_edges) - 1)]

    # Add a new column for epoch bins in the DataFrame
    summary_stats['epoch_bin'] = pd.cut(
        summary_stats['epoch'],
        bins=bin_edges,
        labels=bin_labels,
        include_lowest=True
    )

    # Find all gene columns (those with an underscore, e.g., gene_allele)
    gene_cols = [col for col in summary_stats.columns if '_' in col and col not in ['run','epoch','agent_type','count','avg_energy','avg_age','epoch_bin']]
    genes = set('_'.join(col.split('_')[:-1]) for col in gene_cols)

    # Sort agent_types to ensure consistent ordering
    ordered_agent_types = sorted(agent_types)

    for agent_type in ordered_agent_types:
        agent_data = summary_stats[summary_stats['agent_type'] == agent_type]
        for gene in genes:
            # Find all alleles for this gene
            alleles = sorted([float(col.split('_')[-1]) for col in gene_cols if col.startswith(gene + '_')])
            if not alleles:
                continue
            n_alleles = len(alleles)
            expected_freq = 1.0 / n_alleles if n_alleles > 0 else 0
            # Build a matrix: rows are bins, columns are alleles
            deviation_matrix = []
            for bin_label in bin_labels:
                bin_df = agent_data[agent_data['epoch_bin'] == bin_label]
                total = bin_df['count'].sum()
                row = []
                for allele in alleles:
                    col_name = f"{gene}_{allele}"
                    # Remove trailing ".0" from the column name if it's a float with zero decimal part
                    if allele == int(allele):
                        col_name = f"{gene}_{int(allele)}"
                    else:
                        col_name = f"{gene}_{allele}"
                    allele_count = bin_df[col_name].sum() if col_name in bin_df else 0
                    freq = allele_count / total if total > 0 else 0
                    if expected_freq > 0:
                        deviation = 100 * (freq - expected_freq) / expected_freq
                    else:
                        deviation = 0
                    row.append(deviation)
                deviation_matrix.append(row)
            deviation_df = pd.DataFrame(deviation_matrix, index=bin_labels, columns=alleles)
            plt.figure(figsize=(12, 8))
            sns.heatmap(deviation_df, cmap="coolwarm", center=0, annot=False, cbar_kws={'label': '% Deviation from Uniform'}, vmin=-100, vmax=100)
            plt.title(f'Deviation from Uniform Frequency of {gene} by Epoch for {agent_type} Agents')
            plt.xlabel('Gene Values')
            plt.ylabel('Epoch Bins')
            plt.tight_layout()
            output_path = os.path.join(output_dir, f"{agent_type}_{gene}_heatmap.png")
            plt.savefig(output_path, dpi=300)
            plt.close()
            print(f"Saved gene heatmap to {output_path}")

def plot_agent_count_boxplot_by_bins(summary_stats, agent_types, epochs, output_dir):
    """Create a boxplot showing agent number grouped in 10 epoch bins for each agent type using a DataFrame,
    and overlay a line on the 2nd y-axis showing the percentage of runs that reached each epoch bin with all agent types present."""
    if not epochs:
        return

    # Define bins and labels
    min_epoch = 1
    max_epoch = epochs
    bin_edges = np.linspace(min_epoch, max_epoch, 11)
    bin_labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(bin_edges) - 1)]

    # Add a new column for epoch bins in the DataFrame
    summary_stats['epoch_bin'] = pd.cut(
        summary_stats['epoch'], 
        bins=bin_edges, 
        labels=bin_labels, 
        include_lowest=True
    )

    # Sort agent_types to ensure consistent ordering
    ordered_agent_types = sorted(agent_types)
    
    # Create a consistent color palette based on ordered agent types
    color_palette = dict(zip(ordered_agent_types, sns.color_palette("tab10", len(ordered_agent_types))))

    # Calculate the percentage of runs that reached each epoch bin with all agent types present
    run_percentages = []
    total_runs = summary_stats['run'].nunique()
    
    for bin_label in bin_labels:
        # For each bin, find runs where all agent types are present
        bin_data = summary_stats[summary_stats['epoch_bin'] == bin_label]
        runs_with_all_agents = []
        
        for run_id in bin_data['run'].unique():
            run_data = bin_data[bin_data['run'] == run_id]
            # Check if all agent types are present in this run for this bin
            if set(run_data['agent_type'].unique()) == set(ordered_agent_types):
                runs_with_all_agents.append(run_id)
        
        # Calculate percentage
        percent = (len(runs_with_all_agents) / total_runs) * 100 if total_runs > 0 else 0
        run_percentages.append(percent)

    # Prepare data for boxplot with side-by-side agent types
    plt.figure(figsize=(14, 8))
    ax1 = plt.gca()  # Primary y-axis
    
    # Get data ready for seaborn's boxplot with side-by-side groups
    data_for_plot = summary_stats[summary_stats['agent_type'].isin(ordered_agent_types)].copy()
    
    # Use seaborn's boxplot with the hue parameter for side-by-side boxes
    sns.boxplot(
        x='epoch_bin',
        y='count',
        hue='agent_type',
        data=data_for_plot,
        palette=color_palette,
        width=0.8,
        ax=ax1,
        dodge=True
    )

    # Customize primary y-axis
    ax1.set_yscale('log')  # Use log scale for the y-axis
    ax1.set_xlabel('Epoch Bins')
    ax1.set_ylabel('Agent Number (Log Scale)')
    ax1.set_title('Boxplot of Agent Number by Epoch Bins')
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_xticks(range(len(bin_labels)))
    ax1.set_xticklabels(bin_labels)

    # Move legend to a better position
    ax1.legend(title="Agent Type")

    # Add secondary y-axis for run percentages
    ax2_color = '#AEC6CF'  # Pastel blue
    ax2 = ax1.twinx()
    ax2.plot(range(len(bin_labels)), run_percentages, color=ax2_color, marker='o', linestyle='-', label='Run Percentage')
    ax2.set_ylabel('Percentage of Runs (%)', color=ax2_color)
    ax2.tick_params(axis='y', labelcolor=ax2_color)
    ax2.set_ylim(0, 100)

    # Add legend for the secondary y-axis
    lines, labels = ax1.get_legend_handles_labels()
    line2, label2 = ax2.get_legend_handles_labels()
    ax2.legend(line2, label2, loc='upper right')

    # Finalize and save plot
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'agent_count_boxplot_by_bins.png'))
    plt.close()

def plot_agent_X_boxplot_by_bins(summary_stats, agent_types, epochs, output_dir, row_name, y_label, title):
    """Create a boxplot showing agent X grouped in 10 epoch bins for each agent type using a DataFrame."""
    if not epochs:
        return

    # Define bins and labels
    min_epoch = 1
    max_epoch = epochs
    bin_edges = np.linspace(min_epoch, max_epoch, 11)
    bin_labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(bin_edges) - 1)]

    # Add a new column for epoch bins in the DataFrame
    summary_stats['epoch_bin'] = pd.cut(
        summary_stats['epoch'],
        bins=bin_edges,
        labels=bin_labels,
        include_lowest=True
    )

    # Sort agent_types to ensure consistent ordering
    ordered_agent_types = sorted(agent_types)
    
    # Create a consistent color palette based on ordered agent types
    color_palette = dict(zip(ordered_agent_types, sns.color_palette("tab10", len(ordered_agent_types))))

    # Prepare data for boxplot with side-by-side agent types
    plt.figure(figsize=(14, 8))
    ax = plt.gca()
    
    # Get data ready for seaborn's boxplot with side-by-side groups
    data_for_plot = summary_stats[summary_stats['agent_type'].isin(ordered_agent_types)].copy()
    
    # Use seaborn's boxplot with the hue parameter for side-by-side boxes
    sns.boxplot(
        x='epoch_bin',
        y=row_name,
        hue='agent_type',
        data=data_for_plot,
        palette=color_palette,
        width=0.8,
        ax=ax,
        dodge=True
    )

    ax.set_xlabel('Epoch Bins')
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(title="Agent Type")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{row_name}_boxplot_by_bins.png'))
    plt.close()


def plot_agent_energy_boxplot_by_bins(summary_stats, agent_types, epochs, output_dir):
    plot_agent_X_boxplot_by_bins(
        summary_stats, 
        agent_types, 
        epochs, 
        output_dir, 
        row_name='avg_energy', 
        y_label='Average Energy', 
        title='Boxplot of Agent Average Energy by Epoch Bins'
    )
    return

def plot_agent_age_boxplot_by_bins(summary_stats, agent_types, epochs, output_dir):
    plot_agent_X_boxplot_by_bins(
        summary_stats, 
        agent_types, 
        epochs, 
        output_dir, 
        row_name='avg_age', 
        y_label='Average Age', 
        title='Boxplot of Agent Average Age by Epoch Bins'
    )
    return


def write_summary_data(summary_stats, output_dir="plots"):
    """Write summary data to CSV files using pandas DataFrame"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the entire summary_stats DataFrame to a CSV file
    summary_file = os.path.join(output_dir, 'summary_stats.csv')
    summary_stats.to_csv(summary_file, index=False)
    print(f"Summary statistics saved to {summary_file}")
    

def main():
    global args
    args = parse_arguments()

    yaml_file_path = ""

    if args.summary_csv:
        yaml_file_path = Path(args.summary_csv).parent
        summary_stats = pd.read_csv(args.summary_csv)
        max_epoch = summary_stats['epoch'].max()
    else:
        yaml_file_path = Path(args.file).with_suffix(".plots").resolve()
        yaml_config = load_yaml_config(args.file)
        summary_stats, max_epoch = analyze_data(args.csv_files, yaml_config)
        write_summary_data(summary_stats, output_dir=yaml_file_path)

    create_plots(summary_stats, max_epoch, output_dir=yaml_file_path)

if __name__ == "__main__":
    main()