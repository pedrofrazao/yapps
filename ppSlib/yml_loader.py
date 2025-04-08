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
        arena = ArenaSyncModel(rows, cols)

        for agent_config in arena_config['agents']:
            agent_type = agent_config['type']
            agent_mainclass = agent_config.get('class','LivingAgent')
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

            for _ in range(count):
                kwargs = {}
                kwargs['actions'] = actions
                if alleles is not None:
                    kwargs['chromosome'] = alleles

                # Create the agent instance
                agent = agent_class(arena=arena, state_args=attributes, **kwargs)
                arena.add_to_random_position(agent)

        return arena
