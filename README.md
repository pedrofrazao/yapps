# ppS #

# GTD section #

## correct test execution ##

- [ ] test case with `be_test.py`

python ppSlib/run_all_tests.py

 


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
