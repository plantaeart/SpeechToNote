# SpeechToNote — dev scripts

Command-line helpers for the local Docker, MongoDB, FastAPI and kind workflows.

## Setup

```bash
uv sync
```

## Run

Each script runs from the repository root:

```bash
uv run --project scripts python scripts/infra_local/up.py            # whole stack
uv run --project scripts python scripts/infra_local/down.py
uv run --project scripts python scripts/docker/docker_image_manager.py status
uv run --project scripts python scripts/docker/docker_container_manager.py status
uv run --project scripts python scripts/kubernetes/start.py
```

The Typer CLIs (`docker/*_manager.py`, `infra_local/up.py`, `infra_local/down.py`)
support `--help` and subcommands. The `kubernetes/`, `mongodb_local/` and
`fastapi_local/` scripts are plain scripts: they prompt for what they need and
have no flags.

## What they do

| Script | Purpose |
| --- | --- |
| `infra_local/up.py` | Build and start the compose stack, wait until the API answers |
| `infra_local/down.py` | Stop the stack (`--volumes` also drops the data) |
| `docker/docker_image_manager.py` | Build, run, delete and inspect the app images |
| `docker/docker_container_manager.py` | Start, stop, restart, delete and tail containers |
| `mongodb_local/run_mongodb_docker.py` | Run MongoDB in a container |
| `fastapi_local/run_fastapi.py` | Run the FastAPI backend locally |
| `kubernetes/start.py` | Create the kind cluster, build images and deploy |
| `kubernetes/forwarding.py` | Port-forward the frontend (8080) and API (8081) |
| `kubernetes/kill_forwarding.py` | Stop only the port-forwards this project started |
| `kubernetes/update.py` | Rebuild and reload the deployed images |
| `kubernetes/stop.py` | Delete the kind cluster |

## Tests

```bash
uv run pytest
```