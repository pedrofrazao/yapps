# yappS #

# GTD section #

## correct test execution ##

- [ ] test case with `be_test.py`

python3 ppSlib/run_all_tests.py

python3 -m unittest  discover 

# Tests #

```
RUNID="after2_7e950fd"
DATADIR="data/eq_vs_ne_vs_rand"
RUNCOUNT=500
EPOCHS=250
RUNDIR="rabbit_fox2_random"
YML=rabbit_fox2_random.yml
DOUT="${DATADIR}/${RUNDIR}"
mkdir -p ${DOUT}
source ./bin/activate
for((I=100;I<(($RUNCOUNT+100));I=I+1));  do ./ppS-cli.py --epochs $EPOCHS --batch -f ${DATADIR}/${YML} | tee ${DOUT}/${RUNID}_${YML}-${I}.csv; done
~/.venvs/yapps/bin/python3 ./run_stats.py --num-epochs $EPOCHS -o ${DOUT} ${DOUT}/${RUNID}_${YML}*.csv
```

Or better

```
ppS-cli.py --batch -f data/simple/rabbit.yml --parallel 4 --epochs 50 --runs 50 --progress
```

## gen plots ##

```
plot_simulation.py --file rabbit_fox2_equal_priority.yml rabbit_fox2_equal_priority/rabbit_fox2_equal_priority-run-*.csv
```

# performance stats #

```
alias time="$(which time) -f '\t%E real,\t%U user,\t%S sys,\t%K amem,\t%M mmem,\t%Wswapped out'"
time ppS-cli.py --epoch 100 --file big-arena-4actions-100.yml
```

tests done on a: 8 CPU 11th Gen Intel(R) Core(TM) i5-1135G7 @ 2.40GHz, 16GB RAM, Linux Debian 12.
tests done also on: Ryzen 7 3700X 8-Core

tool used: time (GNU Time)
with a single CPU for 100 epochs.

| arena       | agent type  | # agetns | # actions | see | # genes | exec time | memory  | notes                |
|-------------|-------------|----------|-----------|-----|---------|-----------|---------|----------------------|
| 100x100     | LivingAgent | 1k       | 1         | 0   | 0       | 0:01.58   | 18.9MB  |                      |
| 500x500     | LivingAgent | 25k      | 1         | 0   | 0       | 0:47.82   | 89.8MB  |                      |
| 1000x1000   | LivingAgent | 100k     | 1         | 0   | 0       | 4:09.18   | 313.3MB |                      |
| 10000x10000 | LivingAgent | 10M      | 1         | 0   | 0       | -         | -       | out of memory        |
| 100x100     | LivingAgent | 1k       | 1         | 2   | 0       | 0:02:60   | 18.8MB  |                      |
| 500x500     | LivingAgent | 25k      | 1         | 2   | 0       | 1:19.90   | 89.9MB  |                      |
| 1000x1000   | LivingAgent | 100k     | 1         | 2   | 0       | 6:29.37   | 314.5MB |                      |
| 100x100     | LivingAgent | 1k       | 4         | 2   | 0       | 0:03.27   | 19.1MB  |                      |
| 500x500     | LivingAgent | 25k      | 4         | 2   | 0       | 1:37.28   | 90.3MB  |                      |
| 1000x1000   | LivingAgent | 100k     | 4         | 2   | 0       | 7:34.14   | 314.8MB |                      |
| 1000x1000   | LivingAgent | 100k     | 4         | 2   | 0       | 10:44.58  | 430.0MB | Ryzen                |
| 1000x1000   | LivingAgent | 100k     | 4         | 2   | 0       | 10:45.59  | 430.0MB | Ryzen, collectdata 0 |



# yappS-cli use examples #

```
../../ppS-cli.py  --file rf.yml -o arena/rows=10 -o arena/cols=10  --epoch 1  -o arena/agents/type/Rabbit/count=2 -o arena/agents/type/Carrot/count=1 -o arena/agents/type/Rock/count=0 -o arena/agents/type/Fox/count=0
```

---

OLD
```
python3 plot_simulation.py --file data/eq_vs_ne_vs_rand_2/rabbit_fox2.yml  data/eq_vs_ne_vs_rand_2/rabbit_fox2/rabbit_fox2-*.csv
```


## packages ##

### Arena ###

The arena package have the objective to handle the world size and type and to help arena object to move in the world.

The main attributes of the arena class are:
- rows
- columns
- type: [plan, torus]

And should have methods like:
- get_position(x,y): ArenaObjectsList
- del_position(x,y): ArenaObjectsList
- set_position(x,y, ArenaObjectsList )
- add_to_position(x,y, ArenaObject )
- remove_from_position( x,y, ArenaObject ): ArenaObject
- move_object_position(x,y,ArenaObject,dir,length=1): boolean


