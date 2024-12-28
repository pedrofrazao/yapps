class tw_agent:
    """
    A class to represent an agent in the torus world.

    Attributes:
    ----------
    id : int
        Unique identifier for the agent.
    agent_type : str
        Type of the agent.
    creation_epoch : int
        The epoch when the agent was created.
    energy : float
        The energy level of the agent.
    age : int
        The age of the agent.
    opacity : float
        The opacity level of the agent.
    inertia : float
        The inertia of the agent.
    movement : float
        The movement capability of the agent.
    hold : bool
        Whether the agent is holding something.
    color : str
        The color of the agent.
    """

    def __init__(self, id, agent_type, creation_epoch, energy, age, opacity, inertia, movement, hold, color):
        """
        Constructs all the necessary attributes for the agent object.
        """
        self.id = id
        self.agent_type = agent_type
        self.creation_epoch = creation_epoch
        self.energy = energy
        self.age = age
        self.opacity = opacity
        self.inertia = inertia
        self.movement = movement
        self.hold = hold
        self.color = color

    def __str__(self):
        """
        Returns a string representation of the agent.

        Returns:
        -------
        str
            A string representation of the agent.
        """
        return f"Agent(id={self.id}, type={self.agent_type}, creation_epoch={self.creation_epoch}, energy={self.energy}, age={self.age}, opacity={self.opacity}, inertia={self.inertia}, movement={self.movement}, hold={self.hold}, color={self.color})"

