import typer
from rich.console import Console
from scripts.docker.docker_image_commands.core.docker_manager_core import DockerManager

app = typer.Typer(help="🚀 Run Docker containers for SpeechToNote")
console = Console()

@app.command()
def backend(
    tag: str = typer.Option("latest", "--tag", "-t", help="Docker image tag"),
    port: int = typer.Option(8000, "--port", "-p", help="Host port"),
    name: str = typer.Option(None, "--name", "-n", help="Container name")
):
    """🚀 Run FastAPI Backend container"""
    manager = DockerManager()
    manager.run_container("backend", tag, port, name)

@app.command()
def frontend(
    tag: str = typer.Option("latest", "--tag", "-t", help="Docker image tag"),
    port: int = typer.Option(3000, "--port", "-p", help="Host port"),
    name: str = typer.Option(None, "--name", "-n", help="Container name")
):
    """🚀 Run Vue.js Frontend container"""
    manager = DockerManager()
    manager.run_container("frontend", tag, port, name)

if __name__ == "__main__":
    app()