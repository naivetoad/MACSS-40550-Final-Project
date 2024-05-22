# MACSS 40550 Final Project

## Summary
Our model was inspired by [Schelling's segregation model](https://github.com/jmclip/MACSS-40550-ABM/tree/main/2_Schelling/mesa_schelling). Schelling's segregation model is a classic agent-based model that shows that even a slight preference for similar neighbors can lead to a higher degree of isolation than we intuitively expect. 

For our final project, we explore the dynamics of gentrification in an urban environment by simulating how different socioeconomic groups interact and move within a city. Specifically, we are addressing the following questions: How do varying preferences and income levels influence the formation of segregated neighborhoods? Can immigrants, with different socio-economic attributes, integrate into these neighborhoods?


## Return to the original model
This model can be transferred to the original Schelling model by:
1. Setting the `Preference(0:Homophily, 1:travel time)` to 0 to full weight to level of homophily and 0 weight to travel times.


## Files
'agents.py' Sets up the agents and their behavior for each timestep\
`model.py` Sets up the model itself and calls on agents in each time step\
`server.py` Sets up visualization of agents and adjustable variable control bar\
`run.py` Launches and runs the model

## How to run
1. To install dependencies, use pip and the `requirements.txt` file in this directory
   ```python
   $ pip install -r requirements.txt
3. To run the model interactively, run Python `run.py` in this directory
   ```python
   $ python run.py

## Group members (Alphabetical order)
Gregory Ho, Jiaxuan Zhang, Thomas Yan

