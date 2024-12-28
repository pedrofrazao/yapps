from tw_agent import tw_agent
import random
import argparse
from world_io import save_to_yaml, load_from_yaml, save_world_state, load_world_state

class TorusWorld:
    def __init__(self, name=None, rows=None, cols=None, filename=None, state_filename=None):
        """
        Constructs all the necessary attributes for the torus world object.

        Parameters:
        ----------
        name : str, optional
            The name of the torus world.
        rows : int, optional
            The number of rows in the torus world.
        cols : int, optional
            The number of columns in the torus world.
        filename : str, optional
            The YAML file to load the world definition from.
        state_filename : str, optional
            The YAML file to load the world state from.
        """
        self.filename = filename
        if state_filename:
            load_world_state(self, state_filename)
        elif filename:
            load_from_yaml(self, filename)
        else:
            self.name = name
            self.rows = rows
            self.cols = cols
            self.agents = [[None for _ in range(cols)] for _ in range(rows)]  # Grid to store agents

    def get_agent(self, x, y):
        """Get the agent at (x, y) considering the torus wrapping."""
        wrapped_x = x % self.rows
        wrapped_y = y % self.cols
        return self.agents[wrapped_x][wrapped_y]

    def set_agent(self, x, y, agent):
        """Set the agent at (x, y) considering the torus wrapping."""
        wrapped_x = x % self.rows
        wrapped_y = y % self.cols
        self.agents[wrapped_x][wrapped_y] = agent

    def generate_agents(self, n):
        """Generate N agents randomly on the torus world."""
        for _ in range(n):
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            agent = tw_agent(
                id=random.randint(1, 1000),
                agent_type="TypeA",
                creation_epoch=0,
                energy=100.0,
                age=0,
                opacity=1.0,
                inertia=0.5,
                movement=1.0,
                hold=False,
                color="red"
            )
            self.set_agent(x, y, agent)

    def __str__(self):
        """Return a string representation of the torus world."""
        result = [f"TorusWorld: {self.name}"]
        for row in self.agents:
            row_str = ""
            for agent in row:
                if agent is None:
                    row_str += "."
                else:
                    row_str += agent.agent_type[0]  # Use the first character of the agent_type
            result.append(row_str)
        return '\n'.join(result)

def main():
    parser = argparse.ArgumentParser(description="Create or load a TorusWorld.")
    parser.add_argument('--name', type=str, help='The name of the torus world.')
    parser.add_argument('--rows', type=int, help='The number of rows in the torus world.')
    parser.add_argument('--cols', type=int, help='The number of columns in the torus world.')
    parser.add_argument('--filename', type=str, help='The YAML file to load the world definition from.')
    parser.add_argument('--generate', type=int, help='Number of agents to generate randomly.')
    parser.add_argument('--save_state', type=str, help='Filename to save the current world state.')
    parser.add_argument('--load_state', type=str, help='Filename to load the current world state.')

    args = parser.parse_args()

    if args.load_state:
        torus = TorusWorld(state_filename=args.load_state)
    elif args.filename:
        torus = TorusWorld(filename=args.filename)
    else:
        if args.name is None or args.rows is None or args.cols is None:
            parser.error("The --name, --rows, and --cols arguments are required when not loading from a file.")
        torus = TorusWorld(name=args.name, rows=args.rows, cols=args.cols)
        if args.generate:
            torus.generate_agents(args.generate)

    print(torus)

    if args.save_state:
        save_world_state(torus, args.save_state)

if __name__ == "__main__":
    main()