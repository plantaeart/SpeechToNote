import typer
from rich.console import Console
from typing import Optional, List
from .core.docker_container_manager_core import DockerContainerManager

app = typer.Typer(help="🚀 Start Docker containers")
console = Console()

@app.command()
def start(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to start"),
    all_stopped: bool = typer.Option(False, "--all", help="Start all stopped containers")
):
    """🚀 Start stopped Docker containers"""
    manager = DockerContainerManager()
    
    if all_stopped:
        # Get all stopped containers
        stopped_containers = manager.get_containers(stopped_only=True)
        container_names = [c.name for c in stopped_containers] if stopped_containers else None
    else:
        container_names = containers
    
    manager.start_containers(container_names)

if __name__ == "__main__":
    app()
