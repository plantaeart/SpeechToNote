import typer
from rich.console import Console
from typing import Optional, List
from .core.docker_container_manager_core import DockerContainerManager

app = typer.Typer(help="🛑 Stop Docker containers")
console = Console()

@app.command()
def stop(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to stop"),
    force: bool = typer.Option(False, "--force", "-f", help="Force stop containers"),
    all_running: bool = typer.Option(False, "--all", help="Stop all running containers")
):
    """🛑 Stop running Docker containers"""
    manager = DockerContainerManager()
    
    if all_running:
        # Get all running containers
        running_containers = manager.get_containers(running_only=True)
        container_names = [c.name for c in running_containers] if running_containers else None
    else:
        container_names = containers
    
    manager.stop_containers(container_names, force)

if __name__ == "__main__":
    app()
