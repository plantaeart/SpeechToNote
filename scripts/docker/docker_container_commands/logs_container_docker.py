import typer
from rich.console import Console
from .core.docker_container_manager_core import DockerContainerManager

app = typer.Typer(help="📋 View Docker container logs")
console = Console()

@app.command()
def logs(
    container: str = typer.Argument(..., help="Container name or ID"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show")
):
    """📋 View Docker container logs"""
    manager = DockerContainerManager()
    manager.show_logs(container, follow, lines)

if __name__ == "__main__":
    app()
