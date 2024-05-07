# MACSS_40550_Assignment2

## Summary
Our model was modified based on [Schelling's segregation model](https://github.com/jmclip/MACSS-40550-ABM/tree/main/2_Schelling/mesa_schelling) and [Assignment1](https://github.com/naivetoad/MACSS_40550_Assignment1). Schelling's segregation model is a classic agent-based model that shows that even a slight preference for similar neighbors can lead to a higher degree of isolation than we intuitively expect. In this new model, we simulate Cook County. Agents are represented by red and blue circles and placed on a rectangle grid where each cell can hold at most one agent. Agents' happiness depends on the level of homophily of their neighborhoods, as they prefer to be surrounded by neighbors of the same type.\

Additionally, having a city center represented as a black square on the grid, agents' utility now depends on some combination of their travel time from residence to the city center and level of homophily. Moreover, we included an adjustable preference parameter to shift preferences in the utility function with travel time and homophily. Next, we made an agent's happiness threshold dynamic, which increases if being happy on the last move or decreases if being unhappy on the last move. Unhappy agents will relocate to a vacant cell in each model iteration. This process continues until all agents are happy. 

## Changes been made
+ Enlarge the grid to 60x70 blocks mimicking Cook County, where each block represents 1km x 1km block.
+ Add one city center as a fixed agent representing the coordinates of Millennium Park in Cook County. 
+ Create a utility function that computes happiness based on travel time and homophily with an adjustable preference parameter. 
+ Random updating method is used for active agents.
+ Make the happy threshold dynamic, which acts as a learning mechanism. 

## Return to the original model
This model can be transferred to the original Schelling model by:
1. Setting the `Preference(0:Homophily, 1:travel time)` to 0 to full weight to level of homophily and 0 weight to travel times.


## Files
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

### Discussion Notes
Questions for further contemplation - How do we differentiate houses and households on the grid?
- One option is to only visualize houses. Because we are interested in gentrification, and segregation by housing quality
- Another way is to embed Household attributes in housing.

We are looking at segregation of houses (outcome of interest: gentrification), and segregation of households(outcome of interest: Income-based segregation).

What we would like to see, are clusters of neighborhoods that are well-maintained or poorly maintained. (Process we want to simulate)

House prices should be primarily based on *agent's income* and *transactions in the surrounding vicinity*
