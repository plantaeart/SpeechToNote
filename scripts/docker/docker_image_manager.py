import typer
from typing import Optional
from rich.console import Console
from scripts.docker.docker_image_commands.core.docker_image_manager_core import DockerManager

app = typer.Typer(help="🐳 Docker Manager for SpeechToNote")
console = Console()

@app.command()
def build(
    service: str = typer.Argument(..., help="Service to build (backend/frontend)"),
    tag: str = typer.Argument(..., help="Docker image tag"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Build without cache"),
    run_after: bool = typer.Option(False, "--run", help="Run container after build")
):
    """🔨 Build Docker images for SpeechToNote services"""
    manager = DockerManager()
    if not tag:
        console.print("No tag provided", style="red")
        raise typer.Exit(1)
        
    manager.build_image(service, tag, no_cache, run_after)

@app.command()
def run(
    service: str = typer.Argument(..., help="Service to run (backend/frontend)"),
    tag: str = typer.Argument(..., help="Docker image tag"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Host port"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Container name")
):
    """🚀 Run Docker containers for SpeechToNote services"""
    manager = DockerManager()
    if not tag:
        console.print("No tag provided", style="red")
        raise typer.Exit(1)
    
    manager.run_container(service, tag, port, name)

@app.command()
def delete(
    service: str = typer.Argument(..., help="Service to delete (backend/frontend)"),
    tag: str = typer.Argument(..., help="Docker image tag"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete without confirmation"),
):
    """🗑️ Delete Docker images for SpeechToNote services"""
    manager = DockerManager()
    manager.delete_image(service, tag, force)

@app.command()
def status():
    """📊 Show status of all SpeechToNote Docker resources"""
    manager = DockerManager()
    manager.show_status()

if __name__ == "__main__":
    app()