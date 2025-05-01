import yaml
from ppSlib.arena_sync_model import ArenaSyncModel
# from ppSlib.agent import LivingGAAgent
import ppSlib.agent as agentcls
import ppSlib.action as action

class YMLArenaLoader:
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
                    (allele['name'], allele['values'], allele['description'])
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
