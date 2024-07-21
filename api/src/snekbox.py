import os

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

EVAL_URL: str = os.environ.get("EVAL_URL", "http://localhost:8060/eval")


def evaluate(code: str) -> str:
    response = requests.post(EVAL_URL, json={"input": code}, timeout=2)
    return response.json()["stdout"]
