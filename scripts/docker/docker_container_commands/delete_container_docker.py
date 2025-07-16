import typer
from rich.console import Console
from typing import Optional, List
from .core.docker_container_manager_core import DockerContainerManager

app = typer.Typer(help="🗑️ Delete Docker containers")
console = Console()

@app.command()
def delete(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete containers"),
    all_stopped: bool = typer.Option(False, "--all-stopped", help="Delete all stopped containers")
):
    """🗑️ Delete Docker containers"""
    manager = DockerContainerManager()
    
    if all_stopped:
        # Get all stopped containers
        stopped_containers = manager.get_containers(stopped_only=True)
        container_names = [c.name for c in stopped_containers] if stopped_containers else None
    else:
        container_names = containers
    
    manager.delete_containers(container_names, force)

if __name__ == "__main__":
    app()
