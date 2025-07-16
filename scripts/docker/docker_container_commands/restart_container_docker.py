import typer
from rich.console import Console
from typing import Optional, List
from .core.docker_container_manager_core import DockerContainerManager

app = typer.Typer(help="🔄 Restart Docker containers")
console = Console()

@app.command()
def restart(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to restart"),
    all_containers: bool = typer.Option(False, "--all", help="Restart all containers")
):
    """🔄 Restart Docker containers"""
    manager = DockerContainerManager()
    
    if all_containers:
        # Get all containers
        all_containers_list = manager.get_containers()
        container_names = [c.name for c in all_containers_list] if all_containers_list else None
    else:
        container_names = containers
    
    manager.restart_containers(container_names)

if __name__ == "__main__":
    app()
