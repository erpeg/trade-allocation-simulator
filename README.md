# Trade Allocation Simulator

A small distributed Python demo that allocates simulated trade fills across accounts according to a target portfolio split.

The project contains four processes:

- Controller API receives target account weights and trade fills, then assigns each unit to the account furthest below its target allocation.
- AUM simulator periodically generates target account weights.
- Fill simulator generates random trade fills from multiple worker processes.
- Position monitor receives and prints the resulting positions.

## Requirements

- Python 3.12 or newer

## Setup

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Run the demo

Start each command in a separate terminal from the repository root:

```shell
uvicorn controller.main:app --port 8000
uvicorn position_server.main:app --port 8002
python -m aum_server.main
python -m fill_server.main
```

The controller API is available at `http://127.0.0.1:8000`. Current simulated positions can be inspected at `http://127.0.0.1:8000/positions`, and the OpenAPI interface is available at `http://127.0.0.1:8000/docs`.

## Run tests

```shell
python -m pip install -r requirements-dev.txt
pytest
```

This repository is a demonstration project. It does not connect to a broker, place orders, or process real portfolio data.
