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
                "Urban Slums": self.count_urban_slums,
                "Unhappy Residents": self.get_unhappy_agents,
                "Unhappy Immigrant": self.get_unhappy_immigrant,
                "Average Utility": self.get_average_utility,
                "Moran's I": self.calculate_morans_i
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
                resident_income_mean = 30000 + (self.income_variance * 15000)  # Adjust mean income for residents
                income = np.random.lognormal(mean=np.log(resident_income_mean), sigma=0.25, size=1)[0]
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
                immigrant_income_mean = 30000 - (self.income_variance * 15000)  # Adjust mean income for immigrants
                income = np.random.lognormal(mean=np.log(immigrant_income_mean), sigma=0.25, size=1)[0]
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
    
    def calculate_morans_i(self):
        # Create a matrix to store the presence of residents and immigrants
        matrix = np.zeros((self.grid.height, self.grid.width), dtype=int)

        # Populate the matrix
        for cell in self.grid.coord_iter():
            cell_content, (x, y) = cell
            for agent in cell_content:
                if isinstance(agent, Resident) and not isinstance(agent, Immigrant):
                    matrix[y, x] = 1
                elif isinstance(agent, Immigrant):
                    matrix[y, x] = 2

        # Calculate the weights matrix
        weights = self.get_weights_matrix()

        # Calculate Moran's I
        n = matrix.size
        mean = matrix.mean()
        deviation = matrix - mean
        squared_deviation = deviation ** 2
        weights_sum = np.sum(weights)
        numerator = np.sum(deviation * deviation.T * weights)
        denominator = np.sum(squared_deviation) / n
        morans_i = numerator / (denominator * weights_sum)

        return morans_i

    def get_weights_matrix(self):
        weights = np.zeros((self.grid.height, self.grid.width))
        for i in range(self.grid.height):
            for j in range(self.grid.width):
                neighbors = self.grid.get_neighbors((i, j), moore=True, include_center=False, radius=1)
                num_neighbors = len(neighbors)
                for neighbor in neighbors:
                    weights[i, j] += 1 / num_neighbors
        return weights
            
    def get_unhappy_agents(self):
        unhappy_count = sum(1 for agent in self.schedule.agents if isinstance(agent, Resident) and agent.is_unhappy)
        print(f"Unhappy Residents: {unhappy_count}")  # debug, del later
        return unhappy_count

    def get_unhappy_immigrant(self):
        unhappy_i_count = sum(1 for agent in self.schedule.agents if isinstance(agent, Immigrant) and agent.is_unhappy)
        print(f"Unhappy Immigrant: {unhappy_i_count}")  # debug, del later
        return unhappy_i_count

    def get_average_utility(self):
        utilities = [agent.last_utility for agent in self.schedule.agents if isinstance(agent, Resident)]
        avg_utility = np.mean(utilities) if utilities else 0
        print(f"Average Utility: {avg_utility}")  # debug, del later
        return avg_utility
    
    def count_urban_slums(self):
        urban_slum_count = sum(1 for agent in self.schedule.agents if isinstance(agent, UrbanSlum))
        print(f"Number of Urban Slums: {urban_slum_count}")
        return urban_slum_count

class CustomScheduler(mesa.time.BaseScheduler):
    """
    A custom scheduler that activates agents based on their income and level of unhappiness.
    """
    def step(self):
        # List of all agents who are below their happiness threshold
        agents_with_priority = [(agent.income, agent) for agent in self.agents if isinstance(agent, Resident) and agent.last_utility < agent.happiness_threshold]
        # Sort agents by income, highest first
        agents_with_priority.sort(reverse=True, key=lambda x: x[0])

        # Step all House and UrbanSlum agents
        for agent in self.agents:
            if isinstance(agent, House) or isinstance(agent, UrbanSlum):
                agent.step()
        
        # Activate each agent in sorted order
        for _, agent in agents_with_priority:
            agent.step()

        self.steps += 1
        self.time += 1