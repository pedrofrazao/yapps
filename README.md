# ppS #

# GTD section #

## correct test execution ##

- [ ] test case with `be_test.py`

python3 ppSlib/run_all_tests.py

python3 -m unittest  discover 

# Tests #

```
for((I=100;I<200;I=I+1));  do ./ppS-cli.py --epochs 250 --batch -f rabbit_fox2.yml | tee data2/rabbit_fox2v2-250-${I}.csv; done
~/.venvs/yapps/bin/python3 ./data/run_stats.py --num-epochs 250 -o data2/ data2/*.csv
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
