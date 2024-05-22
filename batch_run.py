from model import Gentrification
from mesa import batch_run
import numpy as np
import pandas as pd

# NOTE: You do not need this as a separate file BUT it can be nice to track
# can also call the file and it makes things a little cleaner as it runs

# Here you will have elements that you want to sweep, eg:
# parameters that will remain constant
# parameters you want to vary
parameters = {"height": 20,
              "width": 20,
              "density": 0.6,
              "immigrant_start": 100,
              "immigrant_count": 160,
              "income_variance": np.linspace(0, 1, 3),
              "preference": np.linspace(0, 1, 3)} 

# what to run and what to collect
# iterations is how many runs per parameter value
# max_steps is how long to run the model
results = batch_run(Gentrification, 
                    parameters,
                    iterations=20,  
                    max_steps=300, 
                    data_collection_period=20) #how often do you want to pull the data


## NOTE: to do data collection, you need to be sure your pathway is correct to save this!
# Data collection
# extract data as a pandas Data Frame
pd.DataFrame(results).to_csv("batch_data.csv")