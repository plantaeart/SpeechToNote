import subprocess
import os
import sys
from datetime import datetime

def run_command(cmd, capture_output=False):
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

def get_existing_images():
    """Get list of existing FastAPI images"""
    print("🔍 Recherche des images speechtonote existantes...")
    cmd = "docker images speechtonote --format \"table {{.Repository}}\\t{{.Tag}}\\t{{.CreatedAt}}\\t{{.Size}}\""
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        print("\n📦 Images existantes:")
        print(stdout)
        return True, stdout
    else:
        print("ℹ️ Aucune image speechtonote trouvée")
        return False, ""

def get_available_tags():
    """Get list of available tags for speechtonote images"""
    cmd = "docker images speechtonote --format \"{{.Tag}}\""
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        tags = [tag.strip() for tag in stdout.split('\n') if tag.strip()]
        return tags
    else:
        return []

def get_docker_status():
    """Check if Docker is running"""
    print("🐳 Vérification de Docker...")
    stdout, stderr, returncode = run_command("docker version", capture_output=True)
    
    if returncode != 0:
        print("❌ Docker n'est pas disponible ou n'est pas démarré")
        print("   Assurez-vous que Docker Desktop est lancé")
        return False
    else:
        print("✅ Docker est disponible")
        return True

def check_port_available(port):
    """Check if a port is available"""
    cmd = f"netstat -an | findstr :{port}"
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        return False  # Port is in use
    else:
        return True   # Port is available

def stop_existing_container(container_name):
    """Stop and remove existing container if it exists"""
    print(f"🔍 Vérification du conteneur existant: {container_name}")
    
    # Check if container exists
    check_cmd = f"docker ps -a --filter name=^/{container_name}$ --format \"{{{{.Names}}}}\""
    stdout, stderr, returncode = run_command(check_cmd, capture_output=True)

    if stdout and returncode == 0 and stdout.strip():
        print(f"⚠️ Conteneur {container_name} existe déjà")
        stop_confirm = input("   Voulez-vous l'arrêter et le supprimer? (y/N): ").strip().lower()
        
        if stop_confirm in ['y', 'yes']:
            # Stop container
            print(f"🛑 Arrêt du conteneur {container_name}...")
            stop_cmd = f"docker stop {container_name}"
            run_command(stop_cmd, capture_output=True)
            
            # Remove container
            print(f"🗑️ Suppression du conteneur {container_name}...")
            rm_cmd = f"docker rm {container_name}"
            run_command(rm_cmd, capture_output=True)
            
            print(f"✅ Conteneur {container_name} nettoyé")
            return True
        else:
            return False
    else:
        return True  # No existing container

def run_image(tag, port, container_name, detached=True):
    """Run the Docker image"""
    image_name = f"speechtonote:{tag}"
    
    print(f"\n🚀 Lancement de l'image: {image_name}")
    print(f"📂 Nom du conteneur: {container_name}")
    print(f"🌐 Port: {port}")
    print(f"🔧 Mode: {'Détaché (arrière-plan)' if detached else 'Interactif (premier plan)'}")
    
    # Build docker run command
    cmd_parts = ["docker", "run"]
    
    if detached:
        cmd_parts.append("-d")
    
    cmd_parts.extend([
        "--name", container_name,
        "-p", f"{port}:8000",
        image_name
    ])
    
    cmd = " ".join(cmd_parts)
    
    print(f"\n🔨 Commande: {cmd}")
    print("⏳ Lancement en cours...")
    
    if detached:
        stdout, stderr, returncode = run_command(cmd, capture_output=True)
        
        if returncode == 0:
            print(f"✅ Conteneur {container_name} lancé avec succès!")
            print(f"🌐 API disponible sur: http://localhost:{port}")
            print(f"📖 Documentation: http://localhost:{port}/docs")
            print(f"📊 Pour voir les logs: docker logs {container_name}")
            print(f"🛑 Pour arrêter: docker stop {container_name}")
            return True
        else:
            print(f"❌ Erreur lors du lancement: {stderr}")
            return False
    else:
        print(f"🌐 API sera disponible sur: http://localhost:{port}")
        print(f"📖 Documentation: http://localhost:{port}/docs")
        print("🛑 Appuyez sur Ctrl+C pour arrêter")
        
        try:
            _, stderr, returncode = run_command(cmd)
            return returncode == 0
        except KeyboardInterrupt:
            print("\n🛑 Conteneur arrêté par l'utilisateur")
            return True

def main():
    """Main function"""
    print("🚀 Script de lancement d'image Docker pour SpeechToNote")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    # Show existing images
    has_images, images_output = get_existing_images()
    
    if not has_images:
        print("🚫 Aucune image speechtonote à lancer")
        print("💡 Construisez d'abord une image avec le script build_fastapi_image_docker.py")
        sys.exit(0)
    
    # Get available tags
    available_tags = get_available_tags()
    
    print("\n" + "=" * 60)
    
    # Ask for tag
    print("🏷️ Sélection du tag")
    if available_tags:
        print("Tags disponibles:")
        for i, tag in enumerate(available_tags, 1):
            print(f"  {i}. {tag}")
        print("\nVous pouvez:")
        print("  - Saisir le nom du tag directement")
        print("  - Saisir le numéro correspondant")
    
    while True:
        tag_input = input("\n🔖 Quel tag voulez-vous lancer? ").strip()
        
        if not tag_input:
            print("❌ Le tag ne peut pas être vide")
            continue
        
        # Check if input is a number (index)
        if tag_input.isdigit():
            index = int(tag_input) - 1
            if 0 <= index < len(available_tags):
                tag = available_tags[index]
                break
            else:
                print(f"❌ Numéro invalide. Choisissez entre 1 et {len(available_tags)}")
                continue
        else:
            # Direct tag name
            tag = tag_input
            if tag not in available_tags:
                print(f"⚠️ Tag '{tag}' non trouvé dans les images existantes")
                confirm_unknown = input("   Continuer quand même? (y/N): ").strip().lower()
                if confirm_unknown not in ['y', 'yes']:
                    continue
            break
    
    # Ask for port
    print("\n🌐 Configuration du port")
    while True:
        port_input = input("Port à utiliser (défaut: 8000): ").strip()
        
        if not port_input:
            port = 8000
            break
        
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                break
            else:
                print("❌ Le port doit être entre 1 et 65535")
        except ValueError:
            print("❌ Le port doit être un nombre")
    
    # Check if port is available
    if not check_port_available(port):
        print(f"⚠️ Le port {port} semble être utilisé")
        port_confirm = input("   Continuer quand même? (y/N): ").strip().lower()
        if port_confirm not in ['y', 'yes']:
            sys.exit(0)
    
    # Ask for container name
    print("\n📂 Nom du conteneur")
    default_container_name = f"speechtonote-{tag}"
    container_input = input(f"Nom du conteneur (défaut: {default_container_name}): ").strip()
    container_name = container_input if container_input else default_container_name
    
    # Check for existing container
    if not stop_existing_container(container_name):
        print("🚫 Impossible de continuer avec un conteneur existant")
        sys.exit(0)
    
    # Ask for run mode
    print("\n🔧 Mode de lancement")
    print("1. Détaché (arrière-plan) - Recommandé")
    print("2. Interactif (premier plan)")
    
    while True:
        mode_input = input("Choisissez le mode (1/2, défaut: 1): ").strip()
        
        if not mode_input or mode_input == "1":
            detached = True
            break
        elif mode_input == "2":
            detached = False
            break
        else:
            print("❌ Choisissez 1 ou 2")
    
    # Confirmation
    print(f"\n📋 Résumé:")
    print(f"   Image: speechtonote:{tag}")
    print(f"   Conteneur: {container_name}")
    print(f"   Port: {port}")
    print(f"   Mode: {'Détaché' if detached else 'Interactif'}")
    print(f"   URL: http://localhost:{port}")
    
    confirm = input("\n❓ Confirmer le lancement? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("🚫 Lancement annulé")
        sys.exit(0)
    
    # Run the image
    success = run_image(tag, port, container_name, detached)
    
    if success:
        if detached:
            print(f"\n🎉 Conteneur lancé avec succès!")
            print(f"💡 Commandes utiles:")
            print(f"   docker logs {container_name}")
            print(f"   docker logs -f {container_name}")
            print(f"   docker stop {container_name}")
            print(f"   docker restart {container_name}")
        else:
            print(f"\n🎉 Lancement terminé")
    else:
        print(f"\n💥 Échec du lancement")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Lancement interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)
