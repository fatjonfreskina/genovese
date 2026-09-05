"""Tests build their own SQLite databases and never load local credentials."""

import os

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["DB_USER"] = "test"
os.environ["DB_PASS"] = "test"
os.environ["HOST_NAME"] = "localhost"
os.environ["HOST_PORT"] = "3306"
os.environ["DB_NAME"] = "test"
