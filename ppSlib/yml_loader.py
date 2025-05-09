import yaml
from ppSlib.arena_sync_model import ArenaSyncModel
# from ppSlib.agent import LivingGAAgent
import ppSlib.agent as agentcls
import ppSlib.action as action

# class Simulation:
#     """
#     __iter__() class for simulations
#     at each __next__() call, it returns a new arena object
#     created with the current simulation parameters
#     """


# class YAMLSimulationLoader:
#     @classmethod
#     def load_simulation_from_yml(cls, filepath):
#         """
#         load the simulation parameters from a yaml file
#         create a simulation object from a yaml file and return it
#         """


class ArenaConfig:
    def __init__(self, config):
        self.config = config

    def get_agent_classes(self):
        """
        Retrieve a list of agent classes from the configuration.
        """
        return [agent['class'] for agent in self.config['arena']['agents']]

    def get_agent_actions(self, cls):
        """
        Retrieve a list of agent actions from the configuration for agents of the specified class.
        """
        actions = []
        for agent in self.config['arena']['agents']:
            if agent.get('type') == cls and 'actions' in agent:
                actions.extend([act['name'] for act in agent['actions']])
        return actions

    def get_agent_genes(self, cls=None):
        """
        Retrieve a list of agent genes and their names from the configuration.
        If a class is specified, retrieve only the genes for agents of that class.
        """
        genes = {}
        for agent in self.config['arena']['agents']:
            if cls is None or agent.get('type') == cls:
                if 'alleles' in agent:
                    genes[agent['type']] = [
                        allele['name'] for allele in agent['alleles']
                    ]
        return genes

    def get_nostats_value(self, cls):
        """
        Retrieve the value for the 'nostats' attribute from the configuration.
        """
        return self.config['arena'][cls].get('nostats', False)


class YMLArenaLoader:
    @staticmethod
    def load_yml_config(filepath):
        """
        load the simulation parameters from a yaml file
        create a simulation object from a yaml file and return it
        """
        with open(filepath, 'r') as file:
            config = yaml.safe_load(file)

        return ArenaConfig(config)


    @staticmethod
    def load_arena_from_yml(filepath):
        with open(filepath, 'r') as file:
            config = yaml.safe_load(file)

        arena_config = config['arena']
        rows = arena_config['rows']
        cols = arena_config['cols']
        torus = arena_config.get('torus', True)  # Default to False if not specified
        sync_model = arena_config.get('sync_model', 'OASCycl')
        arena = ArenaSyncModel(rows, cols, torus=torus, sync_model=sync_model)

        for agent_config in arena_config['agents']:
            agent_type = agent_config['type']
            agent_mainclass = agent_config.get('class', 'LivingAgent')
            count = agent_config['count']
            attributes = agent_config['attributes']
            actions = []
            if agent_config.get('actions') is not None:
                actions = [
                    getattr(action, act['name'])(act['params'])
                    for act in agent_config['actions']
                ]
            alleles = None
            if agent_config.get('alleles') is not None:
                alleles = [
                    (allele['name'], allele['values'],
                     allele.get('description', allele['name']))
                    for allele in agent_config['alleles']
                ]

            agent_mainclass = getattr(agentcls, agent_mainclass)
            agent_class = type(agent_type, (agent_mainclass,), {})

            positions = agent_config.get('position', [])
            for i in range(count):
                agentattr = attributes.copy()
                kwargs = {}
                kwargs['actions'] = actions
                if alleles is not None:
                    kwargs['chromosome'] = alleles

                # Create the agent instance
                agent = agent_class(arena=arena, state_args=agentattr, **kwargs)

                # Add agent to a specific position if available, otherwise random
                if i < len(positions):
                    x, y = positions[i]
                    arena.add_to_position(x, y, agent)
                else:
                    arena.add_to_random_position(agent)

        return arena
