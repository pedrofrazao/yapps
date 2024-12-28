import yaml
import random
from tw_agent import tw_agent

def save_to_yaml(world, filename):
    """Save the world definition, agent types with default attribute values, and population dimension by agent type to a YAML file."""
    world_data = {
        'world_definition': {
            'name': world.name,
            'rows': world.rows,
            'cols': world.cols
        },
        'agent_types': {},
        'population': {}
    }

    agent_types = {}

    for row in world.agents:
        for agent in row:
            if agent is not None:
                if agent.agent_type not in agent_types:
                    agent_types[agent.agent_type] = {
                        'default_attributes': {
                            'creation_epoch': agent.creation_epoch,
                            'energy': agent.energy,
                            'age': agent.age,
                            'opacity': agent.opacity,
                            'inertia': agent.inertia,
                            'movement': agent.movement,
                            'hold': agent.hold,
                            'color': agent.color
                        }
                    }
                if agent.agent_type not in world_data['population']:
                    world_data['population'][agent.agent_type] = 0
                world_data['population'][agent.agent_type] += 1

    world_data['agent_types'] = agent_types

    with open(filename, 'w') as file:
        yaml.dump(world_data, file)

def load_from_yaml(world, filename, empty=False):
    """Load the world definition, agent types with default attribute values, and population dimension by agent type from a YAML file."""
    with open(filename, 'r') as file:
        world_data = yaml.safe_load(file)

    world.name = world_data['world_definition']['name']
    world.rows = world_data['world_definition']['rows']
    world.cols = world_data['world_definition']['cols']
    world.agents = [[None for _ in range(world.cols)] for _ in range(world.rows)]

    agent_types = world_data['agent_types']
    population = world_data['population']

    ## Clear the world if empty is True
    if empty:
        return

    # Optionally, you can recreate agents based on the population and agent_types information
    for agent_type, count in population.items():
        default_attributes = agent_types[agent_type]['default_attributes']
        for _ in range(count):
            x = random.randint(0, world.rows - 1)
            y = random.randint(0, world.cols - 1)
            agent = tw_agent(
                id=random.randint(1, 1000),
                agent_type=agent_type,
                creation_epoch=default_attributes['creation_epoch'],
                energy=default_attributes['energy'],
                age=default_attributes['age'],
                opacity=default_attributes['opacity'],
                inertia=default_attributes['inertia'],
                movement=default_attributes['movement'],
                hold=default_attributes['hold'],
                color=default_attributes['color']
            )
            world.set_agent(x, y, agent)

def save_world_state(world, filename):
    """Save the current world state, including the YAML file used to generate the world, and the position and internal state of each agent."""
    world_state = {
        'world_file': world.filename,
        'agents': []
    }

    for x in range(world.rows):
        for y in range(world.cols):
            agent = world.get_agent(x, y)
            if agent is not None:
                agent_data = {
                    'position': ','.join([str(x), str(y)]),
                    'id': agent.id,
                    'type': agent.agent_type,
                    'creation_epoch': agent.creation_epoch,
                    'energy': agent.energy,
                    'age': agent.age,
                    'opacity': agent.opacity,
                    'inertia': agent.inertia,
                    'movement': agent.movement,
                    'hold': agent.hold,
                    'color': agent.color
                }
                world_state['agents'].append(agent_data)

    with open(filename, 'w') as file:
        yaml.dump(world_state, file)

def load_world_state(world, state_filename):
    """Load the current world state, including the YAML file used to generate the world, and the position and internal state of each agent."""
    with open(state_filename, 'r') as file:
        world_state = yaml.safe_load(file)

    world.filename = world_state['world_file']
    load_from_yaml(world, world.filename, empty=True)

    for agent_data in world_state['agents']:
        x, y = map(int, agent_data['position'].split(','))
        agent = tw_agent(
            id=agent_data['id'],
            agent_type=agent_data['type'],
            creation_epoch=agent_data['creation_epoch'],
            energy=agent_data['energy'],
            age=agent_data['age'],
            opacity=agent_data['opacity'],
            inertia=agent_data['inertia'],
            movement=agent_data['movement'],
            hold=agent_data['hold'],
            color=agent_data['color']
        )
        world.set_agent(x, y, agent)