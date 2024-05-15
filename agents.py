import mesa
import numpy as np


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
        self.moved_this_step = False

    def step(self):
        """
        Perform actions during a simulation step.
        """
        # Step 2: Resident evaluates utility based on locational quality and decides whether to stay or move.
        self.calculate_utilities()
        self.decide_to_move()

    def calculate_utilities(self):
        house = self.model.grid.get_cell_list_contents([self.pos])[0]
        locational_quality = house.locational_quality

        # Utility function. Income is just a placeholder for now
        total_utility = (self.model.preference * locational_quality) + ((1 - self.model.preference) * self.income)
        self.update_happiness(total_utility)

    def decide_to_move(self):
        """
        Decide whether to move based on current utility compared to happiness threshold.
        If the current utility is less than the happiness threshold, attempt to move to a better location.
        """
        # Step 3: If unhappy, residents are queued for a move sorted by income
        if self.last_utility < self.happiness_threshold:
            # Attempt to find a better house
            new_position = self.find_new_house()
            if new_position:
                self.model.grid.move_agent(self, new_position)
                self.moved_this_step = True

    def find_new_house(self):
        """
        Find the best house to move to on the entire grid, based on higher locational quality.
        """
        best_position = None
        best_quality = -float('inf')

        # Loop through every cell in the grid to find the best house
        for x in range(self.model.grid.width):
            for y in range(self.model.grid.height):
                pos = (x, y)
                house = self.model.grid.get_cell_list_contents([pos])[0]  # First element since every cell is a house
                if house.locational_quality > best_quality:
                    best_quality = house.locational_quality
                    best_position = pos

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

 

class Immigrant(Resident):
    def __init__(self, unique_id, model, happiness_threshold, income):
        super().__init__(unique_id, model, happiness_threshold, income)
        # Additional immigrant-specific setup, e.g., different happiness_threshold adjustments, endownments, etc.