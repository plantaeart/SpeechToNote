import typer
from rich.console import Console
from scripts.docker.docker_commands.core.docker_manager_core import DockerManager

app = typer.Typer(help="🔨 Build Docker images for SpeechToNote")
console = Console()

@app.command()
def backend(
    tag: str = typer.Option(None, "--tag", "-t", help="Docker image tag"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Build without cache"),
    run_after: bool = typer.Option(False, "--run", help="Run container after build")
):
    """🔨 Build FastAPI Backend image"""
    manager = DockerManager()
    manager.build_image("backend", tag, no_cache, run_after)

@app.command()
def frontend(
    tag: str = typer.Option("latest", "--tag", "-t", help="Docker image tag"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Build without cache"),
    run_after: bool = typer.Option(False, "--run", help="Run container after build")
):
    """🔨 Build Vue.js Frontend image"""
    manager = DockerManager()
    manager.build_image("frontend", tag, no_cache, run_after)

if __name__ == "__main__":
    app()
