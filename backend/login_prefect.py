from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
key = os.getenv("PREFECT_API_KEY")
subprocess.run(["prefect", "cloud", "login", "--key", key])
