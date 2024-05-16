import mesa
import numpy as np
import random


class House(mesa.Agent):
    """
    Construct the House agent class. Represents a house in a neighborhood whose quality is influenced
    by the economic status of surrounding households.
    """

    def __init__(self, unique_id, model, locational_quality):
        """
        Creates a new House instance.

        Args:
            unique_id: An identifier for the house.
            model: The model instance the house belongs to.
            locational_quality: A numeric value representing the initial neighborhood quality.
        """
        super().__init__(unique_id, model)
        self.locational_quality = locational_quality

    def step(self):
        """
        Updates locational quality based on the average income of neighboring households.
        """
        # Step 1: House agent updates locational quality based on the incomes of neighboring households.
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)
        incomes = [agent.income for agent in neighbors if isinstance(agent, Resident)]
        if incomes:
            self.locational_quality = np.mean(incomes)


class Resident(mesa.Agent):
    """
    Construct a residence agent class that includes economic attributes influencing decisions based on
    locational quality and income.
    """

    def __init__(self, unique_id, model, happiness_threshold, income):
        """
        Initialize a Resident agent with socioeconomic characteristics and a happiness threshold.

        Args:
            unique_id: An identifier for the resident.
            model: The model instance the resident belongs to.
            happiness_threshold: Minimum level of utility for the resident to stay put.
            income: Annual income of the resident, influencing their economic decisions.
        """
        super().__init__(unique_id, model)
        self.happiness_threshold = happiness_threshold
        self.income = income
        self.last_utility = 0
        self.failed_move_attempts = 0  # Track failed move attempts
        self.moved_this_step = False  # Track if the agent moved in the current step

    def step(self):
        """
        Perform actions during a simulation step.
        """
        # Step 2: Resident evaluates utility based on locational quality and decides whether to stay or move.
        self.moved_this_step = False
        self.calculate_utilities()
        self.decide_to_move()

    def calculate_utilities(self):
        house = self.model.grid.get_cell_list_contents([self.pos])[0]
        locational_quality = house.locational_quality

        # Normalize income to a factor
        income_factor = self.income / 40000
        # Cap locational quality based on income
        capped_quality = min(locational_quality, income_factor * 100)
        total_utility = (self.model.preference * capped_quality) + ((1 - self.model.preference) * self.income)
        self.update_happiness(total_utility)

    def decide_to_move(self):
        """
        Decide whether to move based on current utility compared to happiness threshold.
        If the current utility is less than the happiness threshold, attempt to move to a better location.
        """
        house = self.model.grid.get_cell_list_contents([self.pos])[0]
        locational_quality = house.locational_quality
        
        # Step 3: If unhappy, residents are queued for a move sorted by income
        # Move if the locational quality is below income
        if locational_quality < self.income:
            new_position = self.find_new_house()
            if new_position:
                self.model.grid.move_agent(self, new_position)
                self.moved_this_step = True
                self.failed_move_attempts = 0
            else:
                self.failed_move_attempts += 1
                if isinstance(self, Immigrant) and self.failed_move_attempts >= 4:
                    self.convert_to_slum()
        else:
            self.moved_this_step = False

    def find_new_house(self):
        """
        Find the best house to move to on the entire grid, based on higher locational quality.
        """
        best_position = None
        best_quality = -float('inf')
        income_factor = self.income / 40000
        quality_threshold = self.income

        potential_positions = []
        
        for x in range(self.model.grid.width):
            for y in range(self.model.grid.height):
                pos = (x, y)
                cell_contents = self.model.grid.get_cell_list_contents(pos)
                house = next((agent for agent in cell_contents if isinstance(agent, House)), None)
                has_resident = any(isinstance(agent, Resident) for agent in cell_contents)
                
                if house and not has_resident:
                    # Add a small randomness to the quality check to avoid clustering
                    random_quality = house.locational_quality + np.random.uniform(-0.1, 0.1) * quality_threshold
                    if house.locational_quality > best_quality and random_quality < self.income:
                        best_quality = house.locational_quality
                        best_position = pos

                    # Collect potential positions based on some quality threshold
                    if house.locational_quality >= quality_threshold * 0.8:  # A threshold to collect houses of interest
                        potential_positions.append(pos)

        # If no best position is found, choose from the potential positions
        if not best_position and potential_positions:
            best_position = random.choice(potential_positions)
            
        return best_position

    def update_happiness(self, total_utility):
        """
        Adjust happiness threshold based on the last utility.
        Positive change increases happiness threshold, negative change decreases it.
        """
        if total_utility > self.last_utility:
            self.happiness_threshold += 0.05 * (1 - self.happiness_threshold)
        elif total_utility < self.last_utility:
            self.happiness_threshold -= 0.05 * (1 - self.happiness_threshold)
        self.last_utility = total_utility

    def convert_to_slum(self):
        # Convert current cell to an urban slum.
        slum = UrbanSlum(self.model, self.pos, self.model.next_id())
        self.model.grid.place_agent(slum, self.pos)
        self.model.schedule.remove(self)

class UrbanSlum(mesa.Agent):
    """
    Represents an urban slum in the model.
    """
    def __init__(self, model, pos, unique_id):
        super().__init__(unique_id, model)
        self.pos = pos
        self.locational_quality = 0  # [TBD] Slums might have minimum locational quality

class Immigrant(Resident):
    def __init__(self, unique_id, model, happiness_threshold, income):
        super().__init__(unique_id, model, happiness_threshold, income)
        self.moved_this_step = False
    
    def step(self):
        """
        Custom step behavior for immigrants, if different from residents.
        """
        self.calculate_utilities()
        self.decide_to_move()