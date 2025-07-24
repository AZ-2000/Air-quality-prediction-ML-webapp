from dotenv import load_dotenv
import os
import subprocess
load_dotenv()
workspace = os.getenv("PREFECT_WORKSPACE")
key = os.getenv("PREFECT_API_KEY")

command = ["prefect", "cloud", "login", "--key", key]
if workspace:
    command.extend(["--workspace", workspace])

subprocess.run(command)
