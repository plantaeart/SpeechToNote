import typer
from rich.console import Console
from scripts.docker.docker_image_commands.core.docker_image_manager_core import DockerManager

app = typer.Typer(help="📊 Show Docker status for SpeechToNote")
console = Console()

@app.command()
def show():
    """📊 Show status of all SpeechToNote Docker resources"""
    manager = DockerManager()
    manager.show_status()

if __name__ == "__main__":
    show()
