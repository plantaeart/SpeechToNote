import subprocess
import os
import typer
from datetime import datetime
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from .service_model import services_registry

console = Console()

class DockerManager:
    def __init__(self):
        self.console = console
        self.services = services_registry
    
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

    def get_project_paths(self, service: str) -> dict:
        """Get project paths for a service"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
        
        service_config = self.services.get(service)
        context_path = os.path.join(project_root, service_config.context_path)
        dockerfile_path = os.path.join(context_path, "Dockerfile")
        
        return {
            "project_root": project_root,
            "context_path": context_path,
            "dockerfile_path": dockerfile_path
        }

    def get_existing_images(self, image_name: str) -> List[Dict[str, str]]:
        """Get list of existing images"""
        cmd = f'docker images {image_name} --format "{{{{.Repository}}}}|{{{{.Tag}}}}|{{{{.CreatedAt}}}}|{{{{.Size}}}}"'
        stdout, stderr, returncode = self.run_command(cmd, capture_output=True)
        
        images = []
        if returncode == 0 and stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) == 4:
                        images.append({
                            "repository": parts[0],
                            "tag": parts[1], 
                            "created": parts[2],
                            "size": parts[3]
                        })
        return images

    def display_images_table(self, images: List[Dict[str, str]], title: str):
        """Display images in a nice table"""
        if not images:
            self.console.print(f"ℹ️ No {title.lower()} found", style="yellow")
            return
        
        table = Table(title=title)
        table.add_column("Repository", style="cyan")
        table.add_column("Tag", style="magenta")
        table.add_column("Created", style="green")
        table.add_column("Size", style="blue")
        
        for image in images:
            table.add_row(
                image["repository"],
                image["tag"], 
                image["created"],
                image["size"]
            )
        
        self.console.print(table)

    def get_containers_using_image(self, image_name: str) -> List[Dict[str, str]]:
        """Get containers using the specified image"""
        cmd = f'docker ps -a --filter ancestor={image_name} --format "{{{{.ID}}}}|{{{{.Names}}}}|{{{{.Status}}}}"'
        stdout, stderr, returncode = self.run_command(cmd, capture_output=True)
        
        containers = []
        if returncode == 0 and stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 3:
                        containers.append({
                            'id': parts[0],
                            'name': parts[1],
                            'status': parts[2]
                        })
        return containers

    def build_image(self, service: str, tag: str, no_cache: bool = False, run_after: bool = False):
        """Build Docker image for a service"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        if not self.services.exists(service):
            self.console.print(f"❌ Unknown service: {service}", style="red")
            self.console.print(f"Available services: {', '.join(self.services.list_services())}", style="yellow")
            raise typer.Exit(1)
        
        if not tag:
            self.console.print("No tag provided", style="red")
            raise typer.Exit(1)
        
        service_config = self.services.get(service)
        paths = self.get_project_paths(service)
        
        # Display service info
        self.console.print(Panel(f"🔨 Building {service_config.name}", style="blue"))
        
        # Check dockerfile exists
        if not os.path.exists(paths["dockerfile_path"]):
            self.console.print(f"❌ Dockerfile not found: {paths['dockerfile_path']}", style="red")
            raise typer.Exit(1)
        
        # Show existing images
        existing_images = self.get_existing_images(service_config.image_name)
        if existing_images:
            self.display_images_table(existing_images, f"Existing {service_config.name} Images")
        
        full_image_name = service_config.get_full_image_name(tag)
        
        # Build command
        build_cmd = f'docker build -t {full_image_name}'
        
        if no_cache:
            build_cmd += " --no-cache"
        
        # Add build args
        for key, value in service_config.build_args.items():
            build_cmd += f' --build-arg {key}={value}'
        
        build_cmd += f' -f "{paths["dockerfile_path"]}" "{paths["context_path"]}"'
        
        # Show build summary
        info_table = Table(title="Build Configuration")
        info_table.add_column("Setting", style="cyan")
        info_table.add_column("Value", style="green")
        info_table.add_row("Service", service_config.name)
        info_table.add_row("Image", full_image_name)
        info_table.add_row("Context", paths["context_path"])
        info_table.add_row("Dockerfile", paths["dockerfile_path"])
        self.console.print(info_table)
        
        if not Confirm.ask("Continue with build?"):
            self.console.print("🚫 Build cancelled", style="yellow")
            raise typer.Exit(0)
        
        # Build the image
        self.console.print(f"🔨 Building {full_image_name}...", style="blue")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Building image...", total=None)
            _, stderr, returncode = self.run_command(build_cmd)
            progress.update(task, completed=True)
        
        if returncode == 0:
            self.console.print(f"✅ Image {full_image_name} built successfully!", style="green")
            
            if run_after or Confirm.ask("Run container now?"):
                self.run_container(service, tag)
        else:
            self.console.print(f"❌ Build failed: {stderr}", style="red")
            raise typer.Exit(1)

    def run_container(self, service: str, tag: str, port: Optional[int] = None, name: Optional[str] = None):
        """Run a Docker container for a service"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        if not self.services.exists(service):
            self.console.print(f"❌ Unknown service: {service}", style="red")
            self.console.print(f"Available services: {', '.join(self.services.list_services())}", style="yellow")
            raise typer.Exit(1)
        
        service_config = self.services.get(service)
        
        self.console.print(Panel(f"🚀 Running {service_config.name}", style="blue"))
        
        # Show existing images
        existing_images = self.get_existing_images(service_config.image_name)
        if existing_images:
            self.display_images_table(existing_images, f"Available {service_config.name} Images")
        
        # Check if image exists
        image_exists = any(img["tag"] == tag for img in existing_images)
        if not image_exists:
            self.console.print(f"⚠️ Image {service_config.get_full_image_name(tag)} not found", style="yellow")
            if not Confirm.ask("Continue anyway?"):
                raise typer.Exit(0)
        
        # Get port
        if not port:
            port = typer.prompt("Host port", default=service_config.default_port, type=int)
        
        # Get container name
        if not name:
            default_name = service_config.get_default_container_name(tag)
            name = Prompt.ask("Container name", default=default_name)
        
        # Check for existing container
        check_cmd = f'docker ps -a --filter name=^/{name}$ --format "{{{{.Names}}}}"'
        stdout, _, _ = self.run_command(check_cmd, capture_output=True)
        
        if stdout and stdout.strip():
            self.console.print(f"⚠️ Container {name} already exists", style="yellow")
            if Confirm.ask("Stop and remove existing container?"):
                self.console.print(f"🛑 Stopping and removing {name}...", style="yellow")
                self.run_command(f"docker stop {name}", capture_output=True)
                self.run_command(f"docker rm {name}", capture_output=True)
            else:
                self.console.print("🚫 Cannot continue with existing container", style="red")
                raise typer.Exit(1)
        
        full_image_name = service_config.get_full_image_name(tag)
        
        # Show run summary
        info_table = Table(title="Run Configuration")
        info_table.add_column("Setting", style="cyan") 
        info_table.add_column("Value", style="green")
        info_table.add_row("Service", service_config.name)
        info_table.add_row("Image", full_image_name)
        info_table.add_row("Container", name)
        info_table.add_row("Port Mapping", f"{port}:{service_config.container_port}")
        self.console.print(info_table)
        
        if not Confirm.ask("Continue with run?"):
            self.console.print("🚫 Run cancelled", style="yellow")
            raise typer.Exit(0)
        
        # Run the container
        self.console.print(f"🚀 Starting container {name}...", style="blue")
        
        result = subprocess.run([
            "docker", "run", "-d",
            "--name", name,
            "-p", f"{port}:{service_config.container_port}",
            full_image_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            self.console.print(f"✅ Container {name} started successfully!", style="green")
            
            # Show access info
            access_panel = Panel(
                f"🌐 Service available at: http://localhost:{port}\n"
                + (f"📖 API docs: http://localhost:{port}/docs" if service == "backend" else ""),
                title="Access Information",
                style="green"
            )
            self.console.print(access_panel)
            
            # Show useful commands
            commands_table = Table(title="Useful Commands")
            commands_table.add_column("Action", style="cyan")
            commands_table.add_column("Command", style="green")
            commands_table.add_row("View logs", f"docker logs {name}")
            commands_table.add_row("Stop container", f"docker stop {name}")
            commands_table.add_row("Remove container", f"docker rm {name}")
            self.console.print(commands_table)
            
        else:
            self.console.print(f"❌ Failed to start container", style="red")
            self.console.print(f"Error: {result.stderr}", style="red")
            raise typer.Exit(1)

    def delete_image(self, service: str, tag: Optional[str] = None, force: bool = False):
        """Delete Docker images for a service"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        if not self.services.exists(service):
            self.console.print(f"❌ Unknown service: {service}", style="red")
            self.console.print(f"Available services: {', '.join(self.services.list_services())}", style="yellow")
            raise typer.Exit(1)
        
        service_config = self.services.get(service)
        
        self.console.print(Panel(f"🗑️ Deleting {service_config.name} Images", style="red"))
        
        # Show existing images
        existing_images = self.get_existing_images(service_config.image_name)
        if not existing_images:
            self.console.print(f"ℹ️ No {service_config.name} images found", style="yellow")
            raise typer.Exit(0)
        
        self.display_images_table(existing_images, f"Existing {service_config.name} Images")
        
        # Get tags to delete
        tags_to_delete = []
        
        if tag:
            if tag not in [img["tag"] for img in existing_images]:
                self.console.print(f"⚠️ Tag '{tag}' not found", style="yellow")
                if not Confirm.ask("Continue anyway?"):
                    raise typer.Exit(0)
            tags_to_delete = [tag]
        else:
            # Interactive selection
            available_tags = [img["tag"] for img in existing_images]
            self.console.print("Available tags:", style="cyan")
            for i, tag_name in enumerate(available_tags, 1):
                self.console.print(f"  {i}. {tag_name}")
            
            while True:
                selection = Prompt.ask("Select tag (number or name)")
                
                if selection.isdigit():
                    index = int(selection) - 1
                    if 0 <= index < len(available_tags):
                        tags_to_delete = [available_tags[index]]
                        break
                    else:
                        self.console.print(f"❌ Invalid number. Choose 1-{len(available_tags)}", style="red")
                elif selection in available_tags:
                    tags_to_delete = [selection]
                    break
                else:
                    self.console.print(f"❌ Tag '{selection}' not found", style="red")
        
        # Confirm deletion
        if not force:
            self.console.print(f"Images to delete: {', '.join(tags_to_delete)}", style="yellow")
            if not Confirm.ask("⚠️ This will also stop and remove associated containers. Continue?"):
                self.console.print("🚫 Deletion cancelled", style="yellow")
                raise typer.Exit(0)
        
        # Delete each tag
        for tag_name in tags_to_delete:
            full_image_name = service_config.get_full_image_name(tag_name)
            
            self.console.print(f"🗑️ Deleting {full_image_name}...", style="blue")
            
            # Check for containers using this image
            containers = self.get_containers_using_image(full_image_name)
            
            if containers:
                self.console.print(f"Found {len(containers)} container(s) using this image", style="yellow")
                
                for container in containers:
                    container_id = container['id']
                    container_name = container['name']
                    
                    self.console.print(f"🗑️ Removing container {container_name}...", style="yellow")
                    self.run_command(f"docker rm -f {container_id}", capture_output=True)
            
            # Delete the image
            cmd = f'docker rmi {"--force" if force else ""} {full_image_name}'
            stdout, stderr, returncode = self.run_command(cmd, capture_output=True)
            
            if returncode == 0:
                self.console.print(f"✅ Deleted {full_image_name}", style="green")
            else:
                self.console.print(f"❌ Failed to delete {full_image_name}: {stderr}", style="red")
        
        # Show remaining images
        remaining_images = self.get_existing_images(service_config.image_name)
        if remaining_images:
            self.display_images_table(remaining_images, f"Remaining {service_config.name} Images")
        else:
            self.console.print(f"ℹ️ No {service_config.name} images remaining", style="green")

    def show_status(self):
        """Show status of all Docker resources"""
        if not self.check_docker():
            raise typer.Exit(1)
        
        self.console.print(Panel("📊 SpeechToNote Docker Status", style="blue"))
        
        for service_key, service_config in self.services.items():
            self.console.print(f"\n🔍 {service_config.name}", style="bold cyan")
            
            # Show images
            images = self.get_existing_images(service_config.image_name)
            if images:
                self.display_images_table(images, f"{service_config.name} Images")
            else:
                self.console.print(f"   No {service_config.name} images found", style="yellow")
            
            # Show containers
            all_containers = []
            for image in images:
                full_name = f"{image['repository']}:{image['tag']}"
                containers = self.get_containers_using_image(full_name)
                all_containers.extend(containers)
            
            if all_containers:
                container_table = Table(title=f"{service_config.name} Containers")
                container_table.add_column("ID", style="cyan")
                container_table.add_column("Name", style="magenta") 
                container_table.add_column("Status", style="green")
                
                for container in all_containers:
                    container_table.add_row(
                        container["id"][:12],
                        container["name"],
                        container["status"]
                    )
                self.console.print(container_table)