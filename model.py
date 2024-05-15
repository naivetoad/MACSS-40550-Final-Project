import mesa
import numpy as np
from agents import Resident, House, Immigrant

class Gentrification(mesa.Model):
    def __init__(self, N, width, height):
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = CustomScheduler(self)
        
        # Step 0: Initialize agents on the grid.
        ## Thomas you can weigh in here. On the functions we spoke about ytd
        incomes = np.random.lognormal(mean=np.log(40000), sigma=0.25, size=N)
        thresholds = np.random.beta(a=2.5, b=2.5, size=N)  # Beta distribution for more bounded range

        for i in range(N):
            income = incomes[i]
            threshold = thresholds[i] * (0.5 - 0.3) + 0.3  # Scale beta distribution to [0.3, 0.5]
            agent = Resident(i, self, threshold, income)
            x, y = self.grid.find_empty()
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

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