import mesa
import numpy as np
from agents import Resident, House, Immigrant

class Gentrification(mesa.Model):
    """
    Create a Gentrification model, focusing on interactions between residents based on income and locational quality.
    """

    def __init__(self, N, width, height):
        super().__init__() 

        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = CustomScheduler(self)

        # Initialize agents
        for i in range(self.num_agents):
            # Create a Resident agent with some income and threshold
            income = np.random.normal(40_000, 10_000)  # Example income distribution - We should ammend this based on some real parameters/distribution
            happiness_threshold = np.random.uniform(0.3, 0.7)  # Example happiness distribution
            agent = Resident(i, self, happiness_threshold, income)
            x, y = self.grid.find_empty()
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

        self.datacollector = mesa.DataCollector(
            agent_reporters={"Income": "income"}  # Collect income (for now)
        )

    def step(self):
        """
        Run one step of the model.
        """
        self.datacollector.collect(self)
        self.schedule.step()

class CustomScheduler(mesa.time.BaseScheduler):
    """
    A custom scheduler that activates agents based on their income and level of unhappiness.
    """
    def step(self):
        # List of all agents who are below their happiness threshold
        agents_with_priority = [(agent.income, agent) for agent in self.agents if agent.last_utility < agent.happiness_threshold]
        # Sort agents by income, highest first
        agents_with_priority.sort(reverse=True, key=lambda x: x[0])

        # Activate each agent in sorted order
        for _, agent in agents_with_priority:
            agent.step()

        self.steps += 1
        self.time += 1