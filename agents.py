import mesa

class House(mesa.Agent):
    """
    Construct the House agent class.
    A House degrades over time, but can be maintained or repaired.
    """

    def __init__(self, unique_id, model, quality=100, maintenance_rate=0, base_decay_rate=0.02):
        """
        Creates a new House instance.

        Args:
            unique_id: An identifier for the house.
            model: The model instance the house belongs to.
            quality: A numeric value representing the initial quality of the house.
            maintenance_rate: How much of the quality can be restored each step.
            base_decay_rate: Base percentage of quality decay per step.
        """
        super().__init__(unique_id, model)
        self.quality = quality
        self.maintenance_rate = maintenance_rate
        self.base_decay_rate = base_decay_rate  # Base decay rate as a percentage

    def step(self):
        """
        Reduce the quality of the house due to natural decay, then apply any maintenance.
        Decay rate increases as quality decreases, simulating accelerated deterioration.
        """
        # Dynamic decay rate: as quality decreases, decay rate increases
        dynamic_decay_rate = self.base_decay_rate * (1 - self.quality / 100)
        decay_amount = dynamic_decay_rate * self.quality

        # Reduce quality by the decay amount
        self.quality -= decay_amount
        if self.quality < 0:
            self.quality = 0  # Ensuring quality doesn't go negative

        # Apply maintenance
        self.quality += self.maintenance_rate
        if self.quality > 99.9:
            self.quality = 99.9  # Ensuring quality doesn't exceed 100%


class Resident(mesa.Agent):
    """
    Construct a residence agent class that includes economic attributes influencing housing maintenance
    alongside existing spatial and social utilities.
    """

    def __init__(self, unique_id, model, agent_type, happiness_threshold, income):
        """
        Initialize a Resident agent with socioeconomic characteristics and a happiness threshold.
        """
        super().__init__(unique_id, model)
        self.type = agent_type
        self.happiness_threshold = happiness_threshold
        self.last_utility = 0
        self.income = income

    def step(self):
        """
        Perform actions during a simulation step.
        """
        self.calculate_utilities()
        self.manage_house()
        self.decide_to_move()

    def calculate_utilities(self):
        """
        Calculate and update utilities based on location and neighborhood.
        """
        distance_to_center = abs(self.pos[0] - 52) + abs(self.pos[1] - 36)
        travel_time = (distance_to_center * 1000) / 30000 * 60
        travel_utility = 60 - travel_time

        if travel_utility < 0:
            normalized_travel_utility = travel_utility / 292
        else:
            normalized_travel_utility = travel_utility / 60

        similar, unsimilar = 0, 0
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, radius=2):
            if neighbor.pos != (52, 36) and isinstance(neighbor, Resident):
                if neighbor.type == self.type:
                    similar += 1
                else:
                    unsimilar += 1

        homophily_utility = (1.2 * similar - unsimilar)
        normalized_homophily_utility = homophily_utility / 24

        total_utility = (self.model.preference * normalized_travel_utility) + ((1 - self.model.preference) * normalized_homophily_utility)
        self.update_happiness(total_utility)

    def manage_house(self):
        """
        Manage and maintain the house quality based on income and house condition.
        """
        home = next((obj for obj in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(obj, House)), None)
        if home:
            maintenance_contribution = self.determine_maintenance_contribution(home.quality)
            home.maintenance_rate = maintenance_contribution  # Set maintenance rate directly

    def determine_maintenance_contribution(self, house_quality):
        """
        Adjust the financial contribution towards housing maintenance based on income and house quality.
        """
        if house_quality < 50:
            return max(5, self.income * 0.01)  # Urgent maintenance if quality is low
        elif self.income < 30000:
            return 1
        elif self.income < 60000:
            return 3
        else:
            return 5

    def decide_to_move(self):
        """
        Decide whether to move based on current utility compared to happiness threshold.
        """
        if self.last_utility < self.happiness_threshold:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1

    def update_happiness(self, total_utility):
        """
        Adjust happiness threshold based on the last utility.
        """
        if total_utility > self.last_utility:
            self.happiness_threshold += 0.05 * (1 - self.happiness_threshold)
        elif total_utility < self.last_utility:
            self.happiness_threshold -= 0.05 * (1 - self.happiness_threshold)
        self.last_utility = total_utility
 

class CityCenter(mesa.Agent):
    """
    Create a city center agent
    """

    def __init__(self, unique_id, model):
        """
        Initialize an agent
        
        Args:
           unique_id: an agent's unique identifier
           model: Schelling segregation model
        """
        super().__init__(unique_id, model)