# eq_vs_ne_vs_rand_7 Test #

base on the stability result with `crf_400_256_4.yml`.


# logs #


```
export EPOCHS=1000
export SIMNAME=crf_400_256_4_Rga
export RUNS=100
time ../../ppS-cli.py --batch -f ${SIMNAME}.yml --parallel 8 --epochs ${EPOCHS} --runs $RUNS --progress
../../plot_simulation.py --file ${SIMNAME}.yml ${SIMNAME}-run*.csv
tar jcf ${SIMNAME}-run.tar.bz2 ${SIMNAME}-run*.csv && rm ${SIMNAME}-run*.csv
echo "==========="
export SIMNAME=crf_400_256_4_Rga_eq
time ../../ppS-cli.py --batch -f ${SIMNAME}.yml --parallel 8 --epochs ${EPOCHS} --runs $RUNS --progress
../../plot_simulation.py --file ${SIMNAME}.yml ${SIMNAME}-run*.csv
tar jcf ${SIMNAME}-run.tar.bz2 ${SIMNAME}-run*.csv && rm ${SIMNAME}-run*.csv
echo "==========="
export SIMNAME=crf_400_256_4_Rga_random
time ../../ppS-cli.py --batch -f ${SIMNAME}.yml --parallel 8 --epochs ${EPOCHS} --runs $RUNS --progress
../../plot_simulation.py --file ${SIMNAME}.yml ${SIMNAME}-run*.csv
tar jcf ${SIMNAME}-run.tar.bz2 ${SIMNAME}-run*.csv && rm ${SIMNAME}-run*.csv
```


## anova tests ##

```
../../anova_test.py -a crf_400_256_4_Rga.yml -b crf_400_256_4_Rga_eq.yml -c crf_400_256_4_Rga_random.yml -ca crf_400_256_4_Rga.plots/summary_stats.csv -cb crf_400_256_4_Rga_eq.plots/summary_stats.csv -cc crf_400_256_4_Rga_random.plots/summary_stats.csv -v see_length
```

or if already fone with the correct data, variable and value

```
../../anova_test.py
Loading data from CSV files...
Data loaded successfully
NaN values in Treatment A: 0
NaN values in Treatment B: 0
NaN values in Treatment C: 0
/home/pedro/devel/yapps/data/eq_vs_ne_vs_rand_7/../../anova_test.py:192: MatplotlibDeprecationWarning: The 'labels' parameter of boxplot() has been renamed 'tick_labels' since Matplotlib 3.9; support for the old name will be dropped in 3.11.
  box = plt.boxplot(data_to_plot, patch_artist=True, labels=['ne priority', 'eq priority', 'random order'])
               0    1    2    3    4
run            1    2    3    4    5
value          2    2    2    2    2
first_epoch  152  205  191  273  217

Normality test results:

   value  shapiro_stat   p_value
0      2      0.953615  0.001447

Normality test results:

   value  shapiro_stat   p_value
0      2      0.946249  0.000474

Normality test results:

   value  shapiro_stat   p_value
0      2      0.990538  0.708041

Ansari-Bradley Test Results a vs b:
[{'value': np.int64(2), 'ansari_stat': np.float64(5440.0), 'p_value': np.float64(0.056613031018088934)}]

Ansari-Bradley Test Results a vs c:
[{'value': np.int64(2), 'ansari_stat': np.float64(4814.5), 'p_value': np.float64(0.24991966352487305)}]

Ansari-Bradley Test Results b vs c:
[{'value': np.int64(2), 'ansari_stat': np.float64(4492.0), 'p_value': np.float64(0.006378672383572872)}]

Levene's test for homogeneity of variances:
Statistic: 10.0358, p-value: 0.0001

Post-hoc Conover a b test results (p-values, Bonferroni corrected):
          1         2
1  1.000000  0.362095
2  0.362095  1.000000

Post-hoc Conover a c test results (p-values, Bonferroni corrected):
              1             2
1  1.000000e+00  6.531256e-09
2  6.531256e-09  1.000000e+00

Post-hoc DSCF test results:
          n         e
n  1.000000  0.360784
e  0.360784  1.000000

Post-hoc DSCF test results:
              n             r
n  1.000000e+00  2.339680e-08
r  2.339680e-08  1.000000e+00
```


# old #

```
export SIMNAME=rabbit_fox2_random
for ((I=1;I<=9;I=I+1))
do echo $I
../../plot_simulation.py --file ${SIMNAME}.yml ${SIMNAME}-run-$I*.csv
grep -v 'run,epoch,agent_type,count' ${SIMNAME}.plots/summary_stats.csv >> ${SIMNAME}.plots/summary_stats_all.csv
done
grep  'run,epoch,agent_type,count' ${SIMNAME}.plots/summary_stats.csv > ${SIMNAME}.plots/summary_stats_final.csv
cat ${SIMNAME}.plots/summary_stats_all.csv >>  ${SIMNAME}.plots/summary_stats_final.csv
```