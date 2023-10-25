# Access environment variables
import os

# Load environment variables from .env file
from dotenv import load_dotenv
from pathlib import Path


ENVS_DIR = Path(__file__).parent.parent / "envs" / "metatrader" / ".env"
load_dotenv(dotenv_path=str(ENVS_DIR))

# Access environment variables
MT5_LOGIN = int(os.getenv("MT5_LOGIN"))
MT5_SERVER = os.getenv("MT5_SERVER")
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
