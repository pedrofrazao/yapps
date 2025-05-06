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
