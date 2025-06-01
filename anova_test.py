#!/usr/bin/env python3

from plot_simulation import load_yaml_config
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import scikit_posthocs as sp


args = None

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="anova test for simulation results")
    parser.add_argument("-a","--file-treatment-a", required=False, help="YAML file that defines the simulation treatment A")
    parser.add_argument("-b","--file-treatment-b", required=False, help="YAML file that defines the simulation treatment B")
    parser.add_argument("-c","--file-treatment-c", required=False, help="YAML file that defines the simulation treatment C")
    parser.add_argument("-ca","--csv-treatment-a", required=False, help="CSV file that contains the results for treatment A")
    parser.add_argument("-cb","--csv-treatment-b", required=False, help="CSV file that contains the results for treatment B")
    parser.add_argument("-cc","--csv-treatment-c", required=False, help="CSV file that contains the results for treatment C")
    parser.add_argument("-v","--variable", required=False, help="variable to test")
    parser.add_argument('-t', '--agent-type', default='Rabbit', help='Type of agent to test (default: Rabbit)')
    parser.add_argument('-pv', '--percentage-value', default=75, help='Percentage of the variable value to test against')
    return parser.parse_args()


def calc_percentages(pd_data, variable, unique_values, agent_type):
    results = []

    for _, row in pd_data.iterrows():
        if row['agent_type'] != agent_type:
            continue
        
        c = lambda v: 0 if pd.isna(v) else int(v)
        # Count total agents of the selected type
        total_agents = sum( c(row[col]) for col in pd_data.columns if col.startswith(f"{variable}_"))
        if total_agents > 0:
            # Calculate percentage for each value of the variable
            for value in unique_values:
                var_col = f"{variable}_{value}"
                if var_col in pd_data.columns:
                    percentage = (row[var_col] / total_agents) * 100 if total_agents > 0 else 0
                    results.append({
                        'run': row['run'],
                        'epoch': row['epoch'],
                        'value': value,
                        'percentage': percentage
                    })

    return pd.DataFrame(results)

def first_epoch_with_percentage_above_threshold(pd_data, threshold):
    """for each run, identify the 1st epoch where the percentage of the value is above the threshold"""
    results = []

    for run in pd_data['run'].unique():
        run_data = pd_data[pd_data['run'] == run]
        for value in run_data['value'].unique():
            value_data = run_data[run_data['value'] == value]
            first_epoch = value_data[value_data['percentage'] > threshold].head(1)
            if not first_epoch.empty:
                results.append({
                    'run': run,
                    'value': value,
                    'first_epoch': first_epoch['epoch'].values[0]
                })

    return pd.DataFrame(results)


def test_normality(pd_data):
    """Perform Shapiro-Wilk test for normality on the first epoch data"""
    results = []
    for value in pd_data['value'].unique():
        value_data = pd_data[pd_data['value'] == value]['first_epoch']
        if len(value_data) > 0:
            stat, p_value = stats.shapiro(value_data)
            results.append({
                'value': value,
                'shapiro_stat': stat,
                'p_value': p_value
            })
    return pd.DataFrame(results)


def test_Ansari_Bradley(d1,d2):
    """Perform Ansari-Bradley"""
    results = []
    for value in d1['value'].unique():
        d1_value = d1[d1['value'] == value]['first_epoch']
        d2_value = d2[d2['value'] == value]['first_epoch']
        if len(d1_value) > 0 and len(d2_value) > 0:
            stat, p_value = stats.ansari(d1_value, d2_value)
            results.append({
                'value': value,
                'ansari_stat': stat,
                'p_value': p_value
            })
    return results


def load_and_process_data( args ):

    if not args.file_treatment_a or not args.file_treatment_b or not args.file_treatment_c:
        # load predefined processed data
        print("Loading data from CSV files...")
        try:
            pd_first_epoch_a = pd.read_csv("a.csv")
            pd_first_epoch_b = pd.read_csv("b.csv")
            pd_first_epoch_c = pd.read_csv("c.csv")
            print("Data loaded successfully")
            return pd_first_epoch_a, pd_first_epoch_b, pd_first_epoch_c
        except FileNotFoundError as e:
            print(f"Error loading data: {e}")
            print("Please provide treatment files and CSV data")
            raise

    treatment_a = load_yaml_config(args.file_treatment_a)
    treatment_b = load_yaml_config(args.file_treatment_b)
    treatment_c = load_yaml_config(args.file_treatment_c)
    pd_a = pd.read_csv(args.csv_treatment_a)
    pd_b = pd.read_csv(args.csv_treatment_b)
    pd_c = pd.read_csv(args.csv_treatment_c)
    variable = args.variable

    # extract the possible values for the variable from the column name that contains the variable name
    variable_pattern = f"{variable}_"
    values_a = [col.replace(variable_pattern, '') for col in pd_a.columns if col.startswith(variable_pattern)]
    values_b = [col.replace(variable_pattern, '') for col in pd_b.columns if col.startswith(variable_pattern)]
    values_c = [col.replace(variable_pattern, '') for col in pd_c.columns if col.startswith(variable_pattern)]

    # Combine unique values from both treatments
    unique_values = list(set(values_a + values_b + values_c))
    print(f"Possible values for variable '{variable}': {unique_values}")

    # for each run and epoch value, and for the agent type selected, calculate the percentage of agents on each variable value
    agent_type = args.agent_type
    pd_perc_a = calc_percentages(pd_a,  variable, unique_values, agent_type)
    pd_perc_b = calc_percentages(pd_b,  variable, unique_values, agent_type)
    pd_perc_c = calc_percentages(pd_c,  variable, unique_values, agent_type)

    # 1st epoch where the percentage of the value is above the threshold
    threshold = args.percentage_value
    pd_first_epoch_a = first_epoch_with_percentage_above_threshold(pd_perc_a, threshold)
    pd_first_epoch_b = first_epoch_with_percentage_above_threshold(pd_perc_b, threshold)
    pd_first_epoch_c = first_epoch_with_percentage_above_threshold(pd_perc_c, threshold)

    pd_first_epoch_a['first_epoch'].plot(kind='kde')

    # Save first epoch data to CSV files
    pd_first_epoch_a.to_csv(f"a.csv", index=False)
    pd_first_epoch_b.to_csv(f"b.csv", index=False)
    pd_first_epoch_c.to_csv(f"c.csv", index=False)

    return pd_first_epoch_a, pd_first_epoch_b, pd_first_epoch_c


def main():
    global args
    args = parse_arguments()

    pd_first_epoch_a, pd_first_epoch_b, pd_first_epoch_c = load_and_process_data(args)

    # check if there is NaN values on the first_epoch
    # Check for NaN values in each dataset
    nan_count_a = pd_first_epoch_a['first_epoch'].isna().sum()
    nan_count_b = pd_first_epoch_b['first_epoch'].isna().sum()
    nan_count_c = pd_first_epoch_c['first_epoch'].isna().sum()

    print(f"NaN values in Treatment A: {nan_count_a}")
    print(f"NaN values in Treatment B: {nan_count_b}")
    print(f"NaN values in Treatment C: {nan_count_c}")

    # Remove NaN values if any
    if nan_count_a > 0 or nan_count_b > 0 or nan_count_c > 0:
        print("Removing NaN values from datasets...")
        pd_first_epoch_a = pd_first_epoch_a.dropna(subset=['first_epoch'])
        pd_first_epoch_b = pd_first_epoch_b.dropna(subset=['first_epoch'])
        pd_first_epoch_c = pd_first_epoch_c.dropna(subset=['first_epoch'])
        print(f"Remaining data points - A: {len(pd_first_epoch_a)}, B: {len(pd_first_epoch_b)}, C: {len(pd_first_epoch_c)}")

    
    # Create boxplot for all three datasets
    data_to_plot = [
        pd_first_epoch_a['first_epoch'],
        pd_first_epoch_b['first_epoch'],
        pd_first_epoch_c['first_epoch']
    ]
    
    plt.figure(figsize=(10, 6))
    box = plt.boxplot(data_to_plot, patch_artist=True, labels=['ne priority', 'eq priority', 'random order'])
    
    # Add some colors to the boxes
    colors = ['lightblue', 'lightgreen', 'lightsalmon']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    
    plt.title(f'Distribution of First Epochs Above {args.percentage_value}%')
    plt.xlabel('Treatment')
    plt.ylabel('Epoch')
    plt.grid(True, linestyle='--', alpha=0.7)
    # plt.show()


    print(pd_first_epoch_a.head().transpose())

    # Check normality for all
    for d in [pd_first_epoch_a, pd_first_epoch_b, pd_first_epoch_c]:
        normality_results = test_normality(d)
        print(f"\nNormality test results:\n")
        print(normality_results)
    
    # Ansari-Bradley test
    ansari_results = test_Ansari_Bradley(pd_first_epoch_a, pd_first_epoch_b)
    print("\nAnsari-Bradley Test Results a vs b:")
    print(ansari_results)

    ansari_results = test_Ansari_Bradley(pd_first_epoch_a, pd_first_epoch_c)
    print("\nAnsari-Bradley Test Results a vs c:")
    print(ansari_results)

    ansari_results = test_Ansari_Bradley(pd_first_epoch_b, pd_first_epoch_c)
    print("\nAnsari-Bradley Test Results b vs c:")
    print(ansari_results)

    # levene test
    stat, p = stats.levene(*[d.to_numpy() for d in data_to_plot], center='median')
    print(f"\nLevene's test for homogeneity of variances:\nStatistic: {stat:.4f}, p-value: {p:.4f}")

    # do the Kruskal-Wallis test
    # data_to_plot = [ pd_first_epoch_a['first_epoch'], pd_first_epoch_b['first_epoch'] ]
    # stat, p = stats.kruskal(*[d.to_numpy() for d in data_to_plot])
    # print(f"\nKruskal-Wallis a b results:")
    # print(f"Statistic: {stat:.4f}, p-value: {p:.4f}")
    # print(f"Significant difference: {'Yes' if p < 0.05 else 'No'}")
    # data_to_plot = [ pd_first_epoch_a['first_epoch'], pd_first_epoch_c['first_epoch'] ]
    # stat, p = stats.kruskal(*[d.to_numpy() for d in data_to_plot])
    # print(f"\nKruskal-Wallis a c results:")
    # print(f"Statistic: {stat:.4f}, p-value: {p:.4f}")
    # print(f"Significant difference: {'Yes' if p < 0.05 else 'No'}")

    data_to_plot = [ pd_first_epoch_a['first_epoch'], pd_first_epoch_b['first_epoch'] ]
    pvalue = sp.posthoc_conover( data_to_plot, p_adjust='bonferroni' )
    print("\nPost-hoc Conover a b test results (p-values, Bonferroni corrected):")
    print(pvalue)

    data_to_plot = [ pd_first_epoch_a['first_epoch'], pd_first_epoch_c['first_epoch'] ]
    pvalue = sp.posthoc_conover( data_to_plot, p_adjust='bonferroni' )
    print("\nPost-hoc Conover a c test results (p-values, Bonferroni corrected):")
    print(pvalue)

    x = pd.DataFrame({"n": pd_first_epoch_a['first_epoch'],
                      "e": pd_first_epoch_b['first_epoch'],
                    })
    x = x.melt(var_name='groups', value_name='values')
    pvalue = sp.posthoc_dscf(x, val_col='values', group_col='groups')
    print(f"\nPost-hoc DSCF test results:\n{pvalue}")

    x = pd.DataFrame({"n": pd_first_epoch_a['first_epoch'],
                      "r": pd_first_epoch_c['first_epoch'],
                    })
    x = x.melt(var_name='groups', value_name='values')
    pvalue = sp.posthoc_dscf(x, val_col='values', group_col='groups')
    print(f"\nPost-hoc DSCF test results:\n{pvalue}")

    return

    # If Kruskal-Wallis shows significant difference, perform post-hoc Dunn's test
    if p < 0.05:
        # Using scipy.posthoc_dunn for pairwise comparisons
        
        # Prepare data for posthoc test
        combined_data = pd.DataFrame({
            'treatment': ['A']*len(pd_first_epoch_a) + ['B']*len(pd_first_epoch_b) + ['C']*len(pd_first_epoch_c),
            'epoch': pd.concat([pd_first_epoch_a['first_epoch'], 
                               pd_first_epoch_b['first_epoch'], 
                               pd_first_epoch_c['first_epoch']])
        })
        
        # Perform Dunn's test
        try:
            posthoc = posthoc_dunn(combined_data, val_col='epoch', group_col='treatment', p_adjust='bonferroni')
            print("\nDunn's post-hoc test (p-values, Bonferroni corrected):")
            print(posthoc)
        except Exception as e:
            print(f"Error performing Dunn's test: {e}")
            print("Consider installing scikit-posthocs with: pip install scikit-posthocs")


    return

    # do the ANOVA test
    print(f"\nANOVA Test for first epoch with {threshold}% of {variable} by {agent_type}")
    print(f"Treatment A: {args.file_treatment_a}")
    print(f"Treatment B: {args.file_treatment_b}")
    print(f"Treatment C: {args.file_treatment_c}")

    # Perform ANOVA test for each unique value of the variable
    for value in unique_values:
        # Filter data for the specific value
        a_data = pd_first_epoch_a[pd_first_epoch_a['value'] == value]
        b_data = pd_first_epoch_b[pd_first_epoch_b['value'] == value]
        c_data = pd_first_epoch_c[pd_first_epoch_c['value'] == value]
        
        if len(a_data) == 0 or len(b_data) == 0 or len(c_data) == 0:
            print(f"\nSkipping ANOVA test for value '{value}' - insufficient data")
            continue
        
        # Perform ANOVA test
        f_stat, p_value = stats.f_oneway(a_data['first_epoch'], b_data['first_epoch'], c_data['first_epoch'])
        
        print(f"\nANOVA test for value: {value}")
        print(f"F-statistic: {f_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        print(f"Significant difference: {'Yes' if p_value < 0.05 else 'No'}")
        
        # Print some descriptive statistics
        a_mean = a_data['first_epoch'].mean()
        b_mean = b_data['first_epoch'].mean()
        c_mean = c_data['first_epoch'].mean()
        a_std = a_data['first_epoch'].std()
        b_std = b_data['first_epoch'].std()
        c_std = c_data['first_epoch'].std()
        
        print(f"Treatment A - Mean first epoch: {a_mean:.2f} (SD: {a_std:.2f})")
        print(f"Treatment B - Mean first epoch: {b_mean:.2f} (SD: {b_std:.2f})")
        print(f"Treatment C - Mean first epoch: {c_mean:.2f} (SD: {c_std:.2f})")



#    print(pd_perc_a.head().transpose())


if __name__ == "__main__":
    main()