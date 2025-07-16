import typer
from rich.console import Console
from scripts.docker.docker_image_commands.core.docker_image_manager_core import DockerManager

app = typer.Typer(help="🗑️ Delete Docker images for SpeechToNote")
console = Console()

@app.command()
def backend(
    tag: str = typer.Option(None, "--tag", "-t", help="Docker image tag"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete without confirmation"),
):
    """🗑️ Delete FastAPI Backend images"""
    manager = DockerManager()
    manager.delete_image("backend", tag, force)

@app.command()
def frontend(
    tag: str = typer.Option(None, "--tag", "-t", help="Docker image tag"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete without confirmation"),
):
    """🗑️ Delete Vue.js Frontend images"""
    manager = DockerManager()
    manager.delete_image("frontend", tag, force)

if __name__ == "__main__":
    app()