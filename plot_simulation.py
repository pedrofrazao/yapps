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

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Generate plots from simulation CSV data")
    parser.add_argument("--file", required=True, help="YAML file that defines the simulation")
    parser.add_argument("--epoch", type=int, required=True, help="Maximum epoch to analyze")
    parser.add_argument("csv_files", nargs="+", help="List of CSV files to load")
    return parser.parse_args()

def load_yaml_config(yaml_path):
    """Load the YAML configuration file using YMLArenaLoader"""
    loader = YMLArenaLoader()
    return loader.load_yml_config(yaml_path)

def extract_data_from_csv(csv_file, max_epoch, arena_config):
    """Extract data from CSV file by parsing its specific format, using ArenaConfig for gene naming"""
    with open(csv_file, 'r') as f:
        content = f.read()
    
    # Find where actual data starts after the grid visualization
    lines = content.splitlines()
    data_start = 0
    for i, line in enumerate(lines):
        if re.match(r'\d+,\w+,\d+,\d+,\d+,.*', line):
            data_start = i
            break
    
    data_lines = lines[data_start:]
    
    # Initialize data structures
    epoch_data = {}
    allele_data = {}
    
    # Get gene mappings from config
    agent_genes = arena_config.get_agent_genes()
    
    for line in data_lines:
        parts = line.split(',')
        if len(parts) >= 6:
            try:
                epoch = int(parts[0])
                if epoch > max_epoch:
                    continue
                    
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
                allele_info = parts[5]
                allele_parts = allele_info.split('|')
                
                allele_data[epoch][agent_type] = defaultdict(lambda: defaultdict(int))
                # Add allele data
                i=0
                for v in allele_parts:
                    allele_data[epoch][agent_type][agent_genes[agent_type][i]][v] += 1
                    i+=1
                    
            except Exception as e:
                print(f"Error processing line: {line} - {e}")
    
    return epoch_data, allele_data

def analyze_data(csv_files, max_epoch, arena_config):
    """Analyze data from multiple CSV files using arena configuration"""
    all_agent_data = {}
    all_allele_data = {}
    
    for csv_file in csv_files:
        agent_data, allele_data = extract_data_from_csv(csv_file, max_epoch, arena_config)
        
        # Merge agent data
        for epoch, epoch_data in agent_data.items():
            if epoch not in all_agent_data:
                all_agent_data[epoch] = defaultdict(list)
            
            for agent_type, agents in epoch_data.items():
                all_agent_data[epoch][agent_type].extend(agents)
        
        # Merge allele data
        for epoch, epoch_alleles in allele_data.items():
            if epoch not in all_allele_data:
                all_allele_data[epoch] = {}
            
            for agent_type, genes in epoch_alleles.items():
                if agent_type not in all_allele_data[epoch]:
                    all_allele_data[epoch][agent_type] = defaultdict(lambda: defaultdict(int))
                
                for gene, alleles in genes.items():
                    for allele, count in alleles.items():
                        all_allele_data[epoch][agent_type][gene][allele] += count
    
    # Calculate summary statistics
    summary_stats = {}
    
    for epoch in range(max_epoch + 1):
        summary_stats[epoch] = {}
        
        # Process agent data
        agent_data = all_agent_data.get(epoch, {})
        for agent_type, agents in agent_data.items():
            if not agents:
                continue
            
            summary_stats[epoch][agent_type] = {
                "count": len(agents),
                "avg_energy": sum(a["energy"] for a in agents) / len(agents),
                "avg_age": sum(a["age"] for a in agents) / len(agents),
                "allele_counts": {}
            }
            
            # Add allele distribution
            if epoch in all_allele_data and agent_type in all_allele_data[epoch]:
                for gene, alleles in all_allele_data[epoch][agent_type].items():
                    summary_stats[epoch][agent_type]["allele_counts"][gene] = dict(alleles)
    
    return summary_stats

def create_plots(summary_stats, output_dir="plots"):
    """Generate plots based on the summary statistics"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Prepare data for plotting - start from epoch 1
    epochs = [e for e in sorted(summary_stats.keys()) if e >= 1]
    if not epochs:
        print("No epoch data starting from epoch 1. Cannot create plots.")
        return
        
    agent_types = set()
    for epoch_data in summary_stats.values():
        agent_types.update(epoch_data.keys())
    agent_types = sorted(agent_types)
    
    # 1. Plot agent count over time
    plt.figure(figsize=(10, 6))
    for agent_type in agent_types:
        counts = [summary_stats[e].get(agent_type, {}).get("count", 0) for e in epochs]
        plt.plot(epochs, counts, label=agent_type)
    
    plt.xlabel('Epoch')
    plt.ylabel('Number of Agents')
    plt.title('Agent Population Over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'agent_count.png'))
    plt.close()
    
    # 2. Plot average energy over time
    plt.figure(figsize=(10, 6))
    for agent_type in agent_types:
        energies = [summary_stats[e].get(agent_type, {}).get("avg_energy", 0) for e in epochs]
        plt.plot(epochs, energies, label=agent_type)
    
    plt.xlabel('Epoch')
    plt.ylabel('Average Energy')
    plt.title('Average Agent Energy Over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'avg_energy.png'))
    plt.close()
    
    # 3. Plot average age over time
    plt.figure(figsize=(10, 6))
    for agent_type in agent_types:
        ages = [summary_stats[e].get(agent_type, {}).get("avg_age", 0) for e in epochs]
        plt.plot(epochs, ages, label=agent_type)
    
    plt.xlabel('Epoch')
    plt.ylabel('Average Age')
    plt.title('Average Agent Age Over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'avg_age.png'))
    plt.close()
    
    # 4. Plot allele distribution for each agent type and gene
    for agent_type in agent_types:
        all_genes = set()
        for epoch_data in summary_stats.values():
            if agent_type in epoch_data and "allele_counts" in epoch_data[agent_type]:
                all_genes.update(epoch_data[agent_type]["allele_counts"].keys())
        
        for gene in all_genes:
            plt.figure(figsize=(12, 7))
            all_alleles = set()
            for epoch in epochs:
                if (agent_type in summary_stats[epoch] and 
                    "allele_counts" in summary_stats[epoch][agent_type] and
                    gene in summary_stats[epoch][agent_type]["allele_counts"]):
                    all_alleles.update(summary_stats[epoch][agent_type]["allele_counts"][gene].keys())
            
            for allele in sorted(all_alleles):
                counts = []
                for epoch in epochs:
                    if (agent_type in summary_stats[epoch] and 
                        "allele_counts" in summary_stats[epoch][agent_type] and
                        gene in summary_stats[epoch][agent_type]["allele_counts"]):
                        counts.append(summary_stats[epoch][agent_type]["allele_counts"][gene].get(allele, 0))
                    else:
                        counts.append(0)
                plt.plot(epochs, counts, label=f'Allele {allele}')
            
            plt.xlabel('Epoch')
            plt.ylabel('Count')
            plt.title(f'Gene {gene} Allele Distribution for {agent_type}')
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(output_dir, f'allele_{agent_type}_{gene}.png'))
            plt.close()
    
    # 5. Plot average age by epoch bins
    plot_age_by_bins(summary_stats, agent_types, epochs, output_dir)
    
    # 6. Plot agent count by epoch bins
    plot_agent_count_by_bins(summary_stats, agent_types, epochs, output_dir)
    
    # 7. Plot average energy by epoch bins
    plot_energy_by_bins(summary_stats, agent_types, epochs, output_dir)
    
    # 8. Plot gene heatmaps showing relative frequency by epoch bins
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
    plt.xticks(x, bin_labels, rotation=45)
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
    """Create heatmaps showing the relative frequency of gene values by epoch bins for each agent type"""
    if not epochs:
        return
        
    min_epoch = max(1, min(epochs))
    max_epoch = max(epochs)
    
    # Use np.linspace for more precise bin boundaries
    bin_edges = np.linspace(min_epoch, max_epoch, 11)
    bins = []
    bin_labels = []
    
    for i in range(10):
        bin_start = int(np.ceil(bin_edges[i]))
        bin_end = int(np.floor(bin_edges[i+1]))
        if i == 9:  # Make sure the last bin includes max_epoch
            bin_end = max_epoch
        
        bins.append((bin_start, bin_end))
        bin_labels.append(f"{bin_start}-{bin_end}")
    
    heatmap_dir = os.path.join(output_dir, "gene_heatmaps")
    os.makedirs(heatmap_dir, exist_ok=True)
    
    for agent_type in agent_types:
        agent_dir = os.path.join(heatmap_dir, f"agent_{agent_type}")
        os.makedirs(agent_dir, exist_ok=True)
        
        all_genes = set()
        for epoch in epochs:
            if (agent_type in summary_stats[epoch] and 
                "allele_counts" in summary_stats[epoch][agent_type]):
                all_genes.update(summary_stats[epoch][agent_type]["allele_counts"].keys())
        
        for gene in all_genes:
            all_alleles = set()
            for epoch in epochs:
                if (agent_type in summary_stats[epoch] and 
                    "allele_counts" in summary_stats[epoch][agent_type] and
                    gene in summary_stats[epoch][agent_type]["allele_counts"]):
                    all_alleles.update(summary_stats[epoch][agent_type]["allele_counts"][gene].keys())
            
            all_alleles = sorted(all_alleles, key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else x)
            
            freq_matrix = np.zeros((len(bins), len(all_alleles)))
            
            for bin_idx, (bin_start, bin_end) in enumerate(bins):
                bin_epochs = [e for e in epochs if bin_start <= e <= bin_end]
                if not bin_epochs:
                    continue
                
                bin_counts = defaultdict( lambda: defaultdict(int) )
                total_agents = defaultdict( lambda: defaultdict(int) )
                
                for epoch in bin_epochs:
                    if (agent_type in summary_stats[epoch] and 
                        "allele_counts" in summary_stats[epoch][agent_type] and
                        gene in summary_stats[epoch][agent_type]["allele_counts"]):
                        
                        for allele, count in summary_stats[epoch][agent_type]["allele_counts"][gene].items():
                            bin_counts[epoch][allele] += count
                            total_agents[epoch][agent_type] += count
                
                for allele_idx, allele in enumerate(all_alleles):
                    if total_agents[epoch][agent_type] > 0: 
                        freq_matrix[bin_idx, allele_idx] = bin_counts[epoch].get(allele, 0) / total_agents[epoch][agent_type]
                    else:
                        freq_matrix[bin_idx, allele_idx] = 0
            
            freq_df = pd.DataFrame(
                freq_matrix, 
                index=bin_labels,
                columns=all_alleles
            )
            
            plt.figure(figsize=(12, 8))
            sns.heatmap(freq_df, cmap="viridis", annot=False, 
                      cbar_kws={'label': 'Relative Frequency'})
            
            plt.title(f'Relative Frequency of {gene} by Epoch for {agent_type} Agents')
            plt.xlabel('Gene Values')
            plt.ylabel('Epoch Bins')
            plt.tight_layout()
            
            output_path = os.path.join(agent_dir, f"{gene}_heatmap.png")
            plt.savefig(output_path, dpi=300)
            plt.close()
            
            print(f"Saved gene heatmap to {output_path}")

def write_summary_data(summary_stats, output_dir="plots"):
    """Write summary data to text files"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    epochs = [e for e in sorted(summary_stats.keys()) if e >= 1]
    if not epochs:
        print("No epoch data starting from epoch 1. Cannot write summary data.")
        return
        
    agent_types = set()
    for epoch_data in summary_stats.values():
        agent_types.update(epoch_data.keys())
    agent_types = sorted(agent_types)
    
    with open(os.path.join(output_dir, 'agent_counts_summary.csv'), 'w') as f:
        f.write("Epoch," + ",".join(agent_types) + "\n")
        for epoch in epochs:
            counts = [str(summary_stats[epoch].get(agent_type, {}).get("count", 0)) for agent_type in agent_types]
            f.write(f"{epoch}," + ",".join(counts) + "\n")
    
    with open(os.path.join(output_dir, 'avg_energy_summary.csv'), 'w') as f:
        f.write("Epoch," + ",".join(agent_types) + "\n")
        for epoch in epochs:
            energies = [str(round(summary_stats[epoch].get(agent_type, {}).get("avg_energy", 0), 2)) for agent_type in agent_types]
            f.write(f"{epoch}," + ",".join(energies) + "\n")
    
    with open(os.path.join(output_dir, 'avg_age_summary.csv'), 'w') as f:
        f.write("Epoch," + ",".join(agent_types) + "\n")
        for epoch in epochs:
            ages = [str(round(summary_stats[epoch].get(agent_type, {}).get("avg_age", 0), 2)) for agent_type in agent_types]
            f.write(f"{epoch}," + ",".join(ages) + "\n")
    
    for agent_type in agent_types:
        all_genes = set()
        for epoch_data in summary_stats.values():
            if agent_type in epoch_data and "allele_counts" in epoch_data[agent_type]:
                all_genes.update(epoch_data[agent_type]["allele_counts"].keys())
        
        for gene in all_genes:
            all_alleles = set()
            for epoch in epochs:
                if (agent_type in summary_stats[epoch] and 
                    "allele_counts" in summary_stats[epoch][agent_type] and
                    gene in summary_stats[epoch][agent_type]["allele_counts"]):
                    all_alleles.update(summary_stats[epoch][agent_type]["allele_counts"][gene].keys())
            
            all_alleles = sorted(all_alleles)
            filename = f'allele_{agent_type}_{gene}_summary.csv'
            with open(os.path.join(output_dir, filename), 'w') as f:
                f.write("Epoch," + ",".join([f"Allele_{a}" for a in all_alleles]) + "\n")
                for epoch in epochs:
                    counts = []
                    for allele in all_alleles:
                        if (agent_type in summary_stats[epoch] and 
                            "allele_counts" in summary_stats[epoch][agent_type] and
                            gene in summary_stats[epoch][agent_type]["allele_counts"]):
                            counts.append(str(summary_stats[epoch][agent_type]["allele_counts"][gene].get(allele, 0)))
                        else:
                            counts.append("0")
                    f.write(f"{epoch}," + ",".join(counts) + "\n")

def main():
    args = parse_arguments()
    
    yaml_config = load_yaml_config(args.file)
    
    summary_stats = analyze_data(args.csv_files, args.epoch, yaml_config)
    
    create_plots(summary_stats)
    
    write_summary_data(summary_stats)

if __name__ == "__main__":
    main()