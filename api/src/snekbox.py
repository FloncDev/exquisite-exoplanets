import requests


def evaluate(code: str) -> str:
    response = requests.post("http://localhost:8060/eval", json={"input": code}, timeout=2)
    return response.json()["stdout"]
