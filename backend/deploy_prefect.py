from pm25_pipeline import pm25_training_pipeline  # your flow function
from dotenv import load_dotenv
import os
from prefect.filesystems import LocalFileSystem

local_file_system_block = LocalFileSystem.load("aqi-block")
load_dotenv()

if __name__ == "__main__":
    pm25_training_pipeline.serve(name="pm25-training-pipeline",  parameters={
            "input_name": "Lahore",
            "datetime_start": "2025-07-05T00:00:00Z",
            "datetime_end": "2025-07-07T00:00:00Z"
        })

   
