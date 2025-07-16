import subprocess
import os
import typer
import time
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from .models import ContainerInfo, container_registry

console = Console()

class DockerContainerManager:
    def __init__(self):
        self.console = console
        self.registry = container_registry
    
    def run_command(self, cmd: str, capture_output: bool = False) -> tuple:
        """Execute a command and return the result"""
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout.strip(), result.stderr.strip(), result.returncode
            else:
                result = subprocess.run(cmd, shell=True, check=True)
                return None, None, 0
        except subprocess.CalledProcessError as e:
            return None, str(e), e.returncode

    def check_docker(self) -> bool:
        """Check if Docker is running"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Checking Docker...", total=None)
            
            stdout, stderr, returncode = self.run_command("docker version", capture_output=True)
            progress.update(task, completed=True)
        
        if returncode != 0:
            self.console.print("❌ Docker is not available or not started", style="red")
            self.console.print("   Make sure Docker Desktop is running", style="yellow")
            return False
        else:
            self.console.print("✅ Docker is available", style="green")
            return True

    def get_containers(self, running_only: bool = False, stopped_only: bool = False) -> List[ContainerInfo]:
        """Get list of containers"""
        if running_only:
            cmd = 'docker ps --format "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}"'
        elif stopped_only:
            cmd = 'docker ps -a --filter "status=exited" --format "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}"'
        else:
            cmd = 'docker ps -a --format "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}"'
        
        stdout, stderr, returncode = self.run_command(cmd, capture_output=True)
        
        containers = []
        if returncode == 0 and stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        containers.append(ContainerInfo(
                            id=parts[0],
                            name=parts[1],
                            image=parts[2],
                            status=parts[3],
                            ports=parts[4] if len(parts) > 4 else None
                        ))
        return containers

    def display_containers_table(self, containers: List[ContainerInfo], title: str):
        """Display containers in a nice table"""
        if not containers:
            self.console.print(f"ℹ️ No {title.lower()} found", style="yellow")
            return
        
        table = Table(title=title)
        table.add_column("Status", style="cyan", width=6)
        table.add_column("Name", style="magenta")
        table.add_column("ID", style="blue", width=12)
        table.add_column("Image", style="green")
        table.add_column("Status Details", style="yellow")
        
        for container in containers:
            table.add_row(
                container.status_icon,
                container.name,
                container.short_id,
                container.image,
                container.status
            )
        
        self.console.print(table)

    def select_containers(self, containers: List[ContainerInfo], operation: str) -> List[ContainerInfo]:
        """Interactive container selection"""
        if not containers:
            return []
        
        self.console.print(f"\n🏷️ Select container(s) to {operation}")
        self.console.print("Available containers:")
        
        for i, container in enumerate(containers, 1):
            self.console.print(f"  {i}. {container.status_icon} {container.name} ({container.short_id})")
            self.console.print(f"     Image: {container.image}")
            self.console.print(f"     Status: {container.status}")
            self.console.print()
        
        self.console.print("Selection options:")
        self.console.print("  - Single number: 1")
        self.console.print("  - Multiple numbers: 1,3,5")
        self.console.print("  - Range: 1-3")
        self.console.print("  - Container names: app,db")
        self.console.print("  - Mixed: 1,app,3-5")
        self.console.print("  - 'all' for all containers")
        
        while True:
            selection = Prompt.ask(f"Which container(s) to {operation}?").strip()
            
            if not selection:
                self.console.print("❌ Selection cannot be empty", style="red")
                continue
            
            selected_containers = self._parse_selection(selection, containers)
            
            if selected_containers:
                return selected_containers
            else:
                self.console.print("❌ No valid containers selected", style="red")

    def _parse_selection(self, selection: str, containers: List[ContainerInfo]) -> List[ContainerInfo]:
        """Parse container selection string"""
        selected = []
        
        if selection.lower() == 'all':
            return containers
        
        parts = [part.strip() for part in selection.split(',')]
        
        for part in parts:
            # Handle range (e.g., "1-3")
            if '-' in part and part.replace('-', '').replace(' ', '').isdigit():
                range_parts = part.split('-')
                if len(range_parts) == 2:
                    try:
                        start = int(range_parts[0].strip())
                        end = int(range_parts[1].strip())
                        for i in range(start, end + 1):
                            if 1 <= i <= len(containers):
                                container = containers[i - 1]
                                if container not in selected:
                                    selected.append(container)
                    except ValueError:
                        continue
            
            # Handle single number
            elif part.isdigit():
                index = int(part) - 1
                if 0 <= index < len(containers):
                    container = containers[index]
                    if container not in selected:
                        selected.append(container)
            
            # Handle name or ID
            else:
                for container in containers:
                    if (part.lower() == container.name.lower() or 
                        part.lower() == container.id.lower() or
                        container.id.startswith(part.lower())):
                        if container not in selected:
                            selected.append(container)
                        break
        
        return selected

    def start_containers(self, container_names: Optional[List[str]] = None):
        """Start stopped containers"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        self.console.print(Panel("🚀 Start Docker Containers", style="blue"))
        
        # Get stopped containers
        all_containers = self.get_containers()
        stopped_containers = [c for c in all_containers if c.is_stopped]
        
        if not stopped_containers:
            self.console.print("ℹ️ No stopped containers found", style="yellow")
            return
        
        self.display_containers_table(stopped_containers, "Stopped Containers")
        
        # Select containers if not specified
        if not container_names:
            selected_containers = self.select_containers(stopped_containers, "start")
        else:
            selected_containers = [c for c in stopped_containers if c.name in container_names]
        
        if not selected_containers:
            self.console.print("🚫 No containers to start", style="yellow")
            return
        
        # Confirm operation
        if not Confirm.ask(f"Start {len(selected_containers)} container(s)?"):
            self.console.print("🚫 Operation cancelled", style="yellow")
            return
        
        # Start containers
        success_count = 0
        for i, container in enumerate(selected_containers, 1):
            self.console.print(f"[{i}/{len(selected_containers)}] 🚀 Starting {container.name}...")
            
            cmd = f'docker start {container.id}'
            _, stderr, returncode = self.run_command(cmd, capture_output=True)
            
            if returncode == 0:
                self.console.print(f"✅ {container.name} started successfully", style="green")
                success_count += 1
                if i < len(selected_containers):
                    time.sleep(1)  # Brief pause between starts
            else:
                self.console.print(f"❌ Failed to start {container.name}: {stderr}", style="red")
        
        self.console.print(f"\n🎉 Started {success_count}/{len(selected_containers)} containers", style="green")

    def stop_containers(self, container_names: Optional[List[str]] = None, force: bool = False):
        """Stop running containers"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        self.console.print(Panel("🛑 Stop Docker Containers", style="red"))
        
        # Get running containers
        all_containers = self.get_containers()
        running_containers = [c for c in all_containers if c.is_running]
        
        if not running_containers:
            self.console.print("ℹ️ No running containers found", style="yellow")
            return
        
        self.display_containers_table(running_containers, "Running Containers")
        
        # Select containers if not specified
        if not container_names:
            selected_containers = self.select_containers(running_containers, "stop")
        else:
            selected_containers = [c for c in running_containers if c.name in container_names]
        
        if not selected_containers:
            self.console.print("🚫 No containers to stop", style="yellow")
            return
        
        # Ask about stop method
        if not force:
            method_choice = Prompt.ask(
                "Stop method", 
                choices=["normal", "force", "auto"], 
                default="normal"
            )
            force = method_choice == "force"
            auto = method_choice == "auto"
        else:
            auto = False
        
        # Confirm operation
        action = "force stop" if force else "stop"
        if not Confirm.ask(f"{action.title()} {len(selected_containers)} container(s)?"):
            self.console.print("🚫 Operation cancelled", style="yellow")
            return
        
        # Stop containers
        success_count = 0
        for i, container in enumerate(selected_containers, 1):
            self.console.print(f"[{i}/{len(selected_containers)}] 🛑 Stopping {container.name}...")
            
            cmd = f'docker {"kill" if force else "stop"} {container.id}'
            _, stderr, returncode = self.run_command(cmd, capture_output=True)
            
            if returncode == 0:
                self.console.print(f"✅ {container.name} stopped successfully", style="green")
                success_count += 1
            elif auto and not force:
                # Try force stop if auto mode and normal stop failed
                self.console.print(f"⚠️ Normal stop failed, trying force stop...", style="yellow")
                cmd = f'docker kill {container.id}'
                _, stderr, returncode = self.run_command(cmd, capture_output=True)
                
                if returncode == 0:
                    self.console.print(f"✅ {container.name} force stopped successfully", style="green")
                    success_count += 1
                else:
                    self.console.print(f"❌ Failed to force stop {container.name}: {stderr}", style="red")
            else:
                self.console.print(f"❌ Failed to stop {container.name}: {stderr}", style="red")
        
        self.console.print(f"\n🎉 Stopped {success_count}/{len(selected_containers)} containers", style="green")

    def restart_containers(self, container_names: Optional[List[str]] = None):
        """Restart containers"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        self.console.print(Panel("🔄 Restart Docker Containers", style="blue"))
        
        # Get all containers
        all_containers = self.get_containers()
        
        if not all_containers:
            self.console.print("ℹ️ No containers found", style="yellow")
            return
        
        self.display_containers_table(all_containers, "All Containers")
        
        # Select containers if not specified
        if not container_names:
            selected_containers = self.select_containers(all_containers, "restart")
        else:
            selected_containers = [c for c in all_containers if c.name in container_names]
        
        if not selected_containers:
            self.console.print("🚫 No containers to restart", style="yellow")
            return
        
        # Confirm operation
        if not Confirm.ask(f"Restart {len(selected_containers)} container(s)?"):
            self.console.print("🚫 Operation cancelled", style="yellow")
            return
        
        # Restart containers
        success_count = 0
        for i, container in enumerate(selected_containers, 1):
            self.console.print(f"[{i}/{len(selected_containers)}] 🔄 Restarting {container.name}...")
            
            cmd = f'docker restart {container.id}'
            _, stderr, returncode = self.run_command(cmd, capture_output=True)
            
            if returncode == 0:
                self.console.print(f"✅ {container.name} restarted successfully", style="green")
                success_count += 1
                if i < len(selected_containers):
                    time.sleep(2)  # Brief pause between restarts
            else:
                self.console.print(f"❌ Failed to restart {container.name}: {stderr}", style="red")
        
        self.console.print(f"\n🎉 Restarted {success_count}/{len(selected_containers)} containers", style="green")

    def delete_containers(self, container_names: Optional[List[str]] = None, force: bool = False):
        """Delete containers"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        self.console.print(Panel("🗑️ Delete Docker Containers", style="red"))
        
        # Get all containers
        all_containers = self.get_containers()
        
        if not all_containers:
            self.console.print("ℹ️ No containers found", style="yellow")
            return
        
        self.display_containers_table(all_containers, "All Containers")
        
        # Select containers if not specified
        if not container_names:
            selected_containers = self.select_containers(all_containers, "delete")
        else:
            selected_containers = [c for c in all_containers if c.name in container_names]
        
        if not selected_containers:
            self.console.print("🚫 No containers to delete", style="yellow")
            return
        
        # Warning for running containers
        running_selected = [c for c in selected_containers if c.is_running]
        if running_selected and not force:
            self.console.print(f"⚠️ {len(running_selected)} running container(s) will be force stopped and deleted", style="yellow")
            force = Confirm.ask("Force delete running containers?", default=False)
            if not force:
                self.console.print("🚫 Operation cancelled", style="yellow")
                return
        
        # Confirm operation
        if not Confirm.ask(f"⚠️ Delete {len(selected_containers)} container(s)? This cannot be undone!"):
            self.console.print("🚫 Operation cancelled", style="yellow")
            return
        
        # Delete containers
        success_count = 0
        for i, container in enumerate(selected_containers, 1):
            self.console.print(f"[{i}/{len(selected_containers)}] 🗑️ Deleting {container.name}...")
            
            force_flag = "-f" if (force or container.is_running) else ""
            cmd = f'docker rm {force_flag} {container.id}'
            _, stderr, returncode = self.run_command(cmd, capture_output=True)
            
            if returncode == 0:
                self.console.print(f"✅ {container.name} deleted successfully", style="green")
                success_count += 1
            else:
                self.console.print(f"❌ Failed to delete {container.name}: {stderr}", style="red")
        
        self.console.print(f"\n🎉 Deleted {success_count}/{len(selected_containers)} containers", style="green")

    def show_logs(self, container_name: str, follow: bool = False, lines: int = 50):
        """Show container logs"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        self.console.print(Panel(f"📋 Container Logs: {container_name}", style="blue"))
        
        # Find container
        containers = self.get_containers()
        container = next((c for c in containers if c.name == container_name or c.id.startswith(container_name)), None)
        
        if not container:
            self.console.print(f"❌ Container '{container_name}' not found", style="red")
            return
        
        # Build logs command
        cmd = f'docker logs'
        if follow:
            cmd += ' -f'
        if lines:
            cmd += f' --tail {lines}'
        cmd += f' {container.id}'
        
        self.console.print(f"📋 Showing logs for {container.name} ({container.short_id})", style="blue")
        
        if follow:
            self.console.print("Press Ctrl+C to stop following logs", style="yellow")
        
        # Execute logs command
        try:
            result = subprocess.run(cmd, shell=True, text=True)
        except KeyboardInterrupt:
            self.console.print("\n🛑 Log following stopped", style="yellow")

    def show_status(self):
        """Show status of all containers"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        self.console.print(Panel("📊 Docker Containers Status", style="blue"))
        
        all_containers = self.get_containers()
        
        if not all_containers:
            self.console.print("ℹ️ No containers found", style="yellow")
            return
        
        running_containers = [c for c in all_containers if c.is_running]
        stopped_containers = [c for c in all_containers if c.is_stopped]
        
        # Summary
        summary_table = Table(title="Container Summary")
        summary_table.add_column("Status", style="cyan")
        summary_table.add_column("Count", style="green")
        summary_table.add_row("🟢 Running", str(len(running_containers)))
        summary_table.add_row("🔴 Stopped", str(len(stopped_containers)))
        summary_table.add_row("📦 Total", str(len(all_containers)))
        self.console.print(summary_table)
        
        # Detailed view
        if all_containers:
            self.display_containers_table(all_containers, "All Containers")
