import mesa
import numpy as np
from agents import Resident, House, Immigrant, UrbanSlum
from mesa.datacollection import DataCollector

class Gentrification(mesa.Model):
    def __init__(self, width, height, density, immigrant_start, immigrant_count=50, income_variance=0.25, preference=0.5):
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = CustomScheduler(self)
        self.immigrant_start = immigrant_start
        self.current_step = 0  # Track the current timestep
        self.immigrant_count = immigrant_count  # Total number of immigrants to add
        self.immigrants_added = 0  # Counter for added immigrants
        self.income_variance = income_variance
        self.preference = preference  # Add preference as an attribute of the model
        self.datacollector = DataCollector(
            model_reporters={
                "Average Income": lambda m: np.mean([a.income for a in m.schedule.agents if isinstance(a, Resident)]),
                "Urban Slums": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, UrbanSlum))
            }
        )
        
        # Prelim - Calculate the total number of agents based on the density
        total_cells = width * height
        num_agents = int(total_cells * density)

        # Step 0a: Initialize houses on every grid
        for x in range(width):
            for y in range(height):
                locational_quality = 0
                house = House(self.next_id(), self, locational_quality)
                self.grid.place_agent(house, (x, y))
                self.schedule.add(house)

        # Step 0b: Initialize agents on the grid.
        # Initialize agents randomly based on density
        placed = 0
        max_attempts = total_cells * 2  # Limit the number of placement attempts to avoid infinite loop
        attempts = 0
        while placed < num_agents and attempts < max_attempts:
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            print(f"Trying to place agent at: x={x}, y={y}")  # Print the random positions for debugging

            cell_contents = self.grid.get_cell_list_contents((x, y))
            has_resident = any(isinstance(agent, Resident) for agent in cell_contents)

            if not has_resident:
                income = np.random.lognormal(mean=np.log(40000 * self.income_variance), sigma=0.25, size=1)[0]
                threshold = np.random.beta(a=2.5, b=2.5, size=1)[0] * 0.2 + 0.3
                agent = Resident(self.next_id(), self, threshold, income)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                placed += 1
            attempts += 1
        print(placed)
        if placed < num_agents:
            print(f"Only placed {placed} agents out of {num_agents} due to density constraints.")

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
                income = np.random.lognormal(mean=np.log(30000 * self.income_variance), sigma=0.3, size=1)[0]
                threshold = np.random.beta(a=2.0, b=3.0, size=1)[0] * 0.2 + 0.3
                immigrant = Immigrant(self.next_id(), self, threshold, income)
                x, y = self.random_empty_cell()
                self.grid.place_agent(immigrant, (x, y))
                self.schedule.add(immigrant)
                self.immigrants_added += 1

    def random_empty_cell(self):
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            print(f"Trying to place immigrant at: x={x}, y={y}")  # Print the random positions for debugging

            cell_contents = self.grid.get_cell_list_contents((x, y))
            has_resident = any(isinstance(agent, Resident) for agent in cell_contents)

            if not has_resident:
                return (x, y)

class CustomScheduler(mesa.time.BaseScheduler):
    """
    A custom scheduler that activates agents based on their income and level of unhappiness.
    """
    def step(self):
        # List of all agents who are below their happiness threshold
        agents_with_priority = [(agent.income, agent) for agent in self.agents if isinstance(agent, Resident) and agent.last_utility < agent.happiness_threshold]
        # Sort agents by income, highest first
        agents_with_priority.sort(reverse=True, key=lambda x: x[0])

        # Activate each agent in sorted order
        for _, agent in agents_with_priority:
            agent.step()

        # Step all House and UrbanSlum agents
        for agent in self.agents:
            if isinstance(agent, House) or isinstance(agent, UrbanSlum):
                agent.step()

        self.steps += 1
        self.time += 1