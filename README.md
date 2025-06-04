# yapps #

yapps stands for Your Arena Predator-Prey System or, maybe...

# Description #

This project has been developed in the context of a master thesis. The resulting system is a work in progress that can be used for simulations but is not a fully developed solution.

*Simulator characteristics*:

- Synchronization schemes:
  - synchronous scheme - all agents operate in parallel.
  - random order scheme - all agents operate in random order.
  - cyclic scheme - all agents operate in a fixed random order at initialization.
- World type:
  - torus
  - bounded
- everything is an agent.
- Activation priority - forces an activation order by agent type.
- Agent volume - it is possible to have more than one agent occupy the same space.
- Agent actions:
  - rest
  - eat
  - mate
    - sexual via chromosome crossover and mutation
    - asexual via cloning
  - escape
  - move
- UI:
  - GUI - to see the agents' movement.
  - CLI - to run simulations in batch.

# Usage #

Some examples of usage.

For the CLI
```
yapps-cli.py  --file rf.yml -o arena/rows=10 -o arena/cols=10  --epoch 10
```

For the GUI
```
yapps.py
```
