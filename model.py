import mesa
import numpy as np

# Storing Global Variables for the different attributes of a home
DECAY_RATES = {
    'plumbing': 0.025,
    'structure': 0.01,
    'environment': 0.05
}

INITIAL_QUALITY = {
    'plumbing': 1.0,
    'structure': 1.0,
    'environment': 1.0
}

ATTRIBUTE_COST_FACTORS = {
    'plumbing': 0.1,   # 10% of the house's market value
    'structure': 0.07, # 7% ...
    'environment': 0.05 # 5% ...
} 

class House(mesa.Agent):
    def __init__(self, unique_id, model, market_value):
        super().__init__(unique_id, model)
        self.quality_attributes = INITIAL_QUALITY.copy()
        self.market_value = market_value # Think about distributing house prices

    def step(self):
        for attr, rate in DECAY_RATES.items():
            self.quality_attributes[attr] = decay_quality(self.quality_attributes[attr], rate)

    def maintain(self):
        total_cost = 0
        for attr, quality in self.quality_attributes.items():
            # Calculate the attribute-specific maintenance cost
            attr_cost = self.market_value * ATTRIBUTE_COST_FACTORS[attr] * (1 - quality)  # Higher cost for lower quality
            total_cost += attr_cost
            # Improve quality based on maintenance
            self.quality_attributes[attr] = min(quality + 0.1, 1)
        # Optionally, increase the market value after maintenance
        self.market_value += total_cost * 0.5 # Increase by what fraction?
        return total_cost

class SchellingAgent(mesa.Agent):
    """
    Construct a residence agent class
    """

    def __init__(self, unique_id, model, agent_type, happiness_threshold, initial_savings):
        """
        Initialize an agent
        
        Args:
           unique_id: an agent's unique identifier
           model: Schelling segregation model
           agent_type: an agent's type (minority=1, majority=0)
           happiness_threshold: an agent's happiness threshold (0.5)
        """
        super().__init__(unique_id, model)
        self.type = agent_type
        self.happiness_threshold = happiness_threshold
        self.last_utility = 0
        self.savings = initial_savings

    def consider_maintenance(self, house):
        '''
        Direct use of maintain method to 'maintain' house
        '''
        if self.savings >= house.maintain():
            # Subtract the cost from the agent's savings
            self.savings -= house.maintain()
            # The market value increase is already handled within the House.maintain method
        else:
            # Handle the case where the agent cannot afford maintenance
            print("Not enough savings for maintenance")

    def step(self):
        '''
        Defines the step function
        '''
        # Find the manhattan distance to the city center (52, 36) in the number of blocks
        # Each block is a 1000m * 1000m square
        distance_to_center = abs(self.pos[0] - 52) + abs(self.pos[1] - 36)
        # Find the travel time from residence to workplace in minutes with a speed of 30000m/h
        travel_time = (distance_to_center * 1000) / 30000 * 60
        # Find the travel utility by subtracting travel time from the Marchetti's constant (30 minutes)
        travel_utility = (30 - travel_time)
        
        # Normalize the travel utility ranging from -322 to 30 (We will explore further augmentations here)
        if travel_utility < 0:
            normalized_travel_utility = travel_utility / 322
        else:
            normalized_travel_utility = travel_utility / 30 

        # Create variables for similar and unsimilar neighborhoods
        similar = 0
        unsimilar = 0
        
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, radius=1):
            # Find the number of similar and unsimilar neighbors in a radius of 1 (8 surrounding blocks)
            if neighbor.pos != (52, 36): # disregard the city center
                if neighbor.type == self.type:
                    similar += 1
                else:
                    unsimilar += 1

        # Find the homophily utility by subtracting the number of unsimilar neighbors from thre number of similar neighbors
        homophily_utility = (similar - unsimilar)
        # Normalize the homophily utility ranging from -8 to 8
        normalized_homophily_utility = homophily_utility / 8 # now scaled between (-1, 1)

        # Find the total utility by adding travel utility and homophily utility in relation to preference toward them
        # Form: u(agent) = theta*u(x) + (1-theta)*u(y)
        total_utility = (self.model.preference * normalized_travel_utility) + (1-self.model.preference) * normalized_homophily_utility
        
        
        # Adjust happiness threshold based on the last utility 
        ## These functions represent the agents dynamic standards when they 
        ## make decisions that impact them positively or negatively. 
        ## Future work will look at different mechanisms of agent learning.
        if total_utility > self.last_utility:
            # Positive feedback: happiness threshold increases 
            self.happiness_threshold += 0.05 * (1 - self.happiness_threshold)
        elif total_utility < self.last_utility:
            # Negative feedback: happiness threshold decreases 
            self.happiness_threshold -= 0.05 * (1 - self.happiness_threshold)

        # Update the last utility for the next move
        self.last_utility = total_utility

        # Update an agent's location
        if total_utility < self.happiness_threshold:
            # An agent mvoes to an empty space if the total utility is smaller than the happiness threshold
            self.model.grid.move_to_empty(self)
        else:
            # Track the number of happy agents
            self.model.happy += 1
            # Track the number of agents happy with travel time
            if normalized_travel_utility > 0:
                self.model.happy_with_travel_time += 1
            # Track the number of agents happy with homophily 
            if normalized_homophily_utility > 0:
                self.model.happy_with_homophily += 1

        # Cosinder Maintainence
        current_home = self.model.grid.get_cell_list_contents([self.pos])
        if isinstance(current_home[0], House):
            self.consider_maintenance(current_home[0])

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

class Schelling(mesa.Model):
    def __init__(
        self,
        height=70,
        width=60,
        density=0.35, # Land use density
        minority_pc=0.35, # Minority percentage
        preference=0.5, # Preference for travel time vs homophily
        initial_savings_range=(1000, 5000), # Range of initial savings for agents
        seed=42,
    ):
        super().__init__(seed=seed)
        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.preference = preference
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "happy": "happy",
                "happy_with_travel_time": "happy_with_travel_time",
                "happy_with_homophily": "happy_with_homophily",
                "average_market_value": lambda m: np.mean([house.market_value for house in m.schedule.agents if isinstance(house, House)]),
                "average_plumbing_quality": lambda m: np.mean([house.quality_attributes['plumbing'] for house in m.schedule.agents if isinstance(house, House)]),
                "average_structure_quality": lambda m: np.mean([house.quality_attributes['structure'] for house in m.schedule.agents if isinstance(house, House)]),
                "average_environment_quality": lambda m: np.mean([house.quality_attributes['environment'] for house in m.schedule.agents if isinstance(house, House)])
            }
        )

        # Place the city center
        city_center = CityCenter(self.next_id(), self)
        self.grid.place_agent(city_center, (52, 36)) # Millennium Park location

         # Initialize agents and houses
        for _, pos in self.grid.coord_iter():
            if self.random.random() < self.density and pos != (52, 36):
                initial_savings = self.random.uniform(*initial_savings_range)
                agent_type = 1 if self.random.random() < self.minority_pc else 0
                happiness_threshold = 0.5
                agent = SchellingAgent(self.next_id(), self, agent_type, happiness_threshold, initial_savings)
                house = House(self.next_id(), self, initial_savings * 10)  # Assuming some relationship between savings and house value, to be ammended later
                
                # Place agent and house in the same cell
                self.grid.place_agent(agent, pos)
                self.grid.place_agent(house, pos)
                self.schedule.add(agent)

        self.datacollector.collect(self)

    def step(self):
        self.happy = 0
        self.happy_with_travel_time = 0
        self.happy_with_homophily = 0
        self.schedule.step()
        self.datacollector.collect(self)
        if self.happy == self.schedule.get_agent_count():
            self.running = False

### Helper functions
def decay_quality(quality, base_rate):
    effective_rate = base_rate + (1 - quality) * 0.5  # Accelerate decay as quality decreases
    return quality * np.exp(-effective_rate)