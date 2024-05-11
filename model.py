import mesa
import numpy as np


class Schelling(mesa.Model):
    """
    Create a Schelling segregation model, representing Cook County population statistics.
    """

    def __init__(
        self,
        height=70,
        width=60,
        density=0.35, # 35% land used for residence in Cook County
        minority_pc=0.35, # 35% minority in Cook County
        preference=0.5,  
        seed=None,
    ):
        """
        Create a new Schelling model.

        Args:
            height, width: grid's size
            density: possibility for a block to be occupied by an agent
            minority_pc: possibility for an agent to be in minority class
            preference: relative preference for travel time and homophily
            seed: seed for reproducibility
        """

        super().__init__() #seed=seed
        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.preference = preference
        self.avg_utility_type0 = 0
        self.avg_utility_type1 = 0

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(width, height, torus=False)

        # Create variables for data collector
        self.happy = 0
        self.datacollector = mesa.DataCollector(model_reporters={"happy": "happy",
                                                                 "avg_utility_type0": "avg_utility_type0",
                                                                 "avg_utility_type1": "avg_utility_type1"})

        # Set up happiness threshold
        happiness_threshold = 0.5

        agent = CityCenter(self.next_id(), self)
        self.grid.place_agent(agent, (52, 36)) # location of the Millennium Park

        # Set up residence agents 
        for _, pos in self.grid.coord_iter():
            if self.random.random() < self.density and pos != (52, 36):
                agent_type = 1 if self.random.random() < self.minority_pc else 0
                agent = Resident(self.next_id(), self, agent_type, happiness_threshold)
                self.grid.place_agent(agent, pos)
                self.schedule.add(agent)

        
                
        self.datacollector.collect(self)

    def step(self):
        """
        Run one step
        """
        # Reset data collector
        self.happy = 0
        self.avg_utility_type0 = 0
        self.avg_utility_type1 = 0

        # Run one step
        self.schedule.step()
        # Collect data
        self.datacollector.collect(self)

        # Stop the simulation if all agents are happy
        if self.happy == self.schedule.get_agent_count():
            self.running = False
