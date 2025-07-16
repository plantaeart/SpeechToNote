import typer
from typing import Optional, List
from rich.console import Console
from rich.prompt import Confirm
from docker_container_commands.core.docker_container_manager_core import DockerContainerManager

app = typer.Typer(help="🐳 Docker Container Manager for SpeechToNote")
console = Console()

@app.command()
def start(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to start"),
    all_stopped: bool = typer.Option(None, "--all", help="Start all stopped containers")
):
    """🚀 Start stopped Docker containers"""
    manager = DockerContainerManager()
    
    # Interactive prompt when parameter not provided
    if not containers and all_stopped is None:
        all_stopped = Confirm.ask("Start all stopped containers?", default=False)
    
    if all_stopped:
        stopped_containers = manager.get_containers(stopped_only=True)
        container_names = [c.name for c in stopped_containers] if stopped_containers else None
    else:
        container_names = containers
    
    manager.start_containers(container_names)

@app.command()
def stop(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to stop"),
    force: bool = typer.Option(None, "--force", "-f", help="Force stop containers"),
    all_running: bool = typer.Option(None, "--all", help="Stop all running containers")
):
    """🛑 Stop running Docker containers"""
    manager = DockerContainerManager()
    
    # Interactive prompts when parameters not provided
    if not containers and all_running is None:
        all_running = Confirm.ask("Stop all running containers?", default=False)
    
    if force is None:
        force = Confirm.ask("Force stop containers?", default=False)
    
    if all_running:
        running_containers = manager.get_containers(running_only=True)
        container_names = [c.name for c in running_containers] if running_containers else None
    else:
        container_names = containers
    
    manager.stop_containers(container_names, force)

@app.command()
def restart(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to restart"),
    all_containers: bool = typer.Option(None, "--all", help="Restart all containers")
):
    """🔄 Restart Docker containers"""
    manager = DockerContainerManager()
    
    # Interactive prompt when parameter not provided
    if not containers and all_containers is None:
        all_containers = Confirm.ask("Restart all containers?", default=False)
    
    if all_containers:
        all_containers_list = manager.get_containers()
        container_names = [c.name for c in all_containers_list] if all_containers_list else None
    else:
        container_names = containers
    
    manager.restart_containers(container_names)

@app.command()
def delete(
    containers: Optional[List[str]] = typer.Argument(None, help="Container names to delete"),
    force: bool = typer.Option(None, "--force", "-f", help="Force delete containers"),
    all_stopped: bool = typer.Option(None, "--all-stopped", help="Delete all stopped containers")
):
    """🗑️ Delete Docker containers"""
    manager = DockerContainerManager()
    
    # Interactive prompts when parameters not provided
    if not containers and all_stopped is None:
        all_stopped = Confirm.ask("Delete all stopped containers?", default=False)
    
    if force is None:
        force = Confirm.ask("Force delete containers?", default=False)
    
    if all_stopped:
        stopped_containers = manager.get_containers(stopped_only=True)
        container_names = [c.name for c in stopped_containers] if stopped_containers else None
    else:
        container_names = containers
    
    manager.delete_containers(container_names, force)

@app.command()
def logs(
    container: str = typer.Argument(..., help="Container name or ID"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show")
):
    """📋 View Docker container logs"""
    manager = DockerContainerManager()
    manager.show_logs(container, follow, lines)

@app.command()
def status():
    """📊 Show status of all Docker containers"""
    manager = DockerContainerManager()
    manager.show_status()

if __name__ == "__main__":
    app()
