# Agent-Based Model of Urban Gentrification

## Project Overview
This project implements an Agent-Based Model inspired by Schelling's 
Segregation Model, extending its application to income-based residential 
dynamics. The model simulates interactions and relocations of different 
socioeconomic groups within a city to study the formation of segregated 
neighborhoods and gentrification.

## Model Description
The simulation operates on a 20x20 grid representing a city where each cell 
contains a static agent, which may be occupied by a dynamic agent.

1. Static Agents: Houses and urban slums with varying locational quality based 
on neighborhood income.
2. Dynamic Agents: Residents and immigrants differ by income and happiness 
threshold.
3. Movement: Dynamic agents can attempt to relocate based on a utility function 
balancing income level and homophily preferences.

## File Structure
| File | Description |
|------|------------|
| `README.md` | Provides an overview and instructions. |
| `agents.py` | Defines agent behaviors. |
| `batch_data.csv` | Data generated from a batch run. |
| `batch_run.py` | Defines parameters for a batch run. |
| `model.py` | Defines agent interactions. |
| `requirements.txt` | Lists necessary dependencies. |
| `run.py` | Runs a server for simulations. |
| `server.py` | Defines interactivity of simulations. |
| `visualization.ipynb` | Analyzes and visualizes batch runs. |

## How to Run
To install dependencies:
```sh
pip install -r requirements.txt
```

To run interactive simulations:
```sh
python run.py
```

To conduct a batch run:
```sh
python batch_run.py
```

## Contributors
- [Ho, Gregory](https://github.com/GregoryHo88)
- [Yan, Weiwu](https://github.com/naivetoad)
- [Zhang, Jiaxuan](https://github.com/Twilight233333)


