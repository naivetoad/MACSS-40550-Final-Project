import mesa
import numpy as np
from agents import Resident, House, Immigrant

class Gentrification(mesa.Model):
    def __init__(self, N, width, height):
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = CustomScheduler(self)
        self.immigrant_start = immigrant_start
        self.current_step = 0  # Track the current timestep
        self.immigrant_count = immigrant_count  # Total number of immigrants to add
        self.immigrants_added = 0  # Counter for added immigrants
        
        # Step 0: Initialize agents on the grid.
        # Initialize agents
        for i in range(self.num_agents):
            ## Thomas you can weigh in here. On the functions we spoke about ytd
            income = np.random.lognormal(mean=np.log(40000), sigma=0.25, size=1)[0]
            threshold = np.random.beta(a=2.5, b=2.5, size=1)[0] * 0.2 + 0.3
            agent = Resident(i, self, threshold, income)
            x, y = self.grid.find_empty()
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

    def step(self):
        # Add immigrants gradually each step after immigrant_start
        if self.current_step >= self.immigrant_start and self.immigrants_added < self.immigrant_count:
            self.add_immigrants(1)  # Add 1 immigrant per step after immigrant_start
        self.schedule.step()
        self.datacollector.collect(self)
        self.current_step += 1

    def add_immigrants(self, number):
        # Function to add a specified number of immigrants
        for _ in range(number):
            if self.immigrants_added < self.immigrant_count:
                ## Thomas you can weigh in here. On the functions we spoke about ytd
                income = np.random.lognormal(mean=np.log(30000), sigma=0.3, size=1)[0]
                threshold = np.random.beta(a=2.0, b=3.0, size=1)[0] * 0.2 + 0.3
                immigrant = Immigrant(self.num_agents + self.immigrants_added, self, threshold, income)
                x, y = self.grid.find_empty()
                self.grid.place_agent(immigrant, (x, y))
                self.schedule.add(immigrant)
                self.immigrants_added += 1

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