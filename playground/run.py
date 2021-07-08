from playground.client import Client
from playground.split_pipeline import SplitPipeline

client = Client()

# Parameters
split_map = {'train': 0.7, 'test': 0.3}
param = 1

# Pipeline
split_pipeline = SplitPipeline(split_map=split_map,
                               param=param)
split_pipeline.run()

