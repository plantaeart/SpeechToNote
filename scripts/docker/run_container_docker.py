import subprocess
import sys

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

def get_available_tags(image_name):
    """Get list of available tags for images"""
    cmd = f"docker images {image_name} --format \"{{{{.Tag}}}}\""
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        tags = [tag.strip() for tag in stdout.split('\n') if tag.strip()]
        return tags
    else:
        return []

def get_existing_images(image_name):
    """Get list of existing images"""
    print(f"🔍 Recherche des images {image_name} existantes...")
    cmd = f"docker images {image_name} --format \"table {{{{.Repository}}}}\\t{{{{.Tag}}}}\\t{{{{.CreatedAt}}}}\\t{{{{.Size}}}}\""
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        print("\n📦 Images existantes:")
        print(stdout)
        return True
    else:
        print(f"ℹ️ Aucune image {image_name} trouvée")
        return False

def choose_service():
    """Let user choose between FastAPI and Vue.js"""
    print("🎯 Choix du service à lancer")
    print("=" * 40)
    print("1. FastAPI (Backend)")
    print("2. Vue.js (Frontend)")
    print("3. Quitter")
    
    while True:
        choice = input("\n🔖 Quel service voulez-vous lancer? (1-3): ").strip()
        
        if choice == "1":
            return "fastapi"
        elif choice == "2":
            return "vuejs"
        elif choice == "3":
            print("👋 Au revoir!")
            sys.exit(0)
        else:
            print("❌ Choix invalide. Veuillez saisir 1, 2 ou 3.")

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
        return True

def run_fastapi_container():
    """Run FastAPI Docker container"""
    print("\n🚀 Lancement du conteneur Docker FastAPI pour SpeechToNote")
    print("=" * 60)
    
    image_name = "speechtonote"
    
    # Show existing images
    has_images = get_existing_images(image_name)
    
    if not has_images:
        print("🚫 Aucune image speechtonote à lancer")
        return False
    
    # Get available tags
    available_tags = get_available_tags(image_name)
    
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
    
    # Ask for container name
    print("\n📂 Nom du conteneur")
    default_container_name = f"speechtonote-{tag}"
    container_input = input(f"Nom du conteneur (défaut: {default_container_name}): ").strip()
    container_name = container_input if container_input else default_container_name
    
    # Check for existing container
    if not stop_existing_container(container_name):
        print("🚫 Impossible de continuer avec un conteneur existant")
        return False
    
    full_image_name = f"{image_name}:{tag}"
    
    # Confirmation
    print(f"\n📋 Configuration:")
    print(f"   Image: {full_image_name}")
    print(f"   Conteneur: {container_name}")
    print(f"   Port: {port}:8000")
    
    confirm = input("\n❓ Confirmer le lancement? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("🚫 Lancement annulé")
        return False
    
    # Run the container
    print(f"🚀 Lancement du conteneur {container_name}...")
    result = subprocess.run([
        "docker", "run", "-d",
        "--name", container_name,
        "-p", f"{port}:8000",
        full_image_name
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Conteneur FastAPI {container_name} démarré avec succès!")
        print(f"🌐 API disponible à: http://localhost:{port}")
        print(f"📖 Documentation: http://localhost:{port}/docs")
        print("")
        print("📋 Commandes utiles:")
        print(f"   • Voir les logs: docker logs {container_name}")
        print(f"   • Arrêter: docker stop {container_name}")
        print(f"   • Supprimer: docker rm {container_name}")
        return True
    else:
        print(f"❌ Échec du démarrage du conteneur FastAPI")
        print(f"💥 Erreur: {result.stderr}")
        return False

def run_vuejs_container():
    """Run Vue.js Docker container"""
    print("\n🚀 Lancement du conteneur Docker Vue.js pour SpeechToNote")
    print("=" * 60)
    
    image_name = "speech-to-note-frontend"
    
    # Show existing images
    has_images = get_existing_images(image_name)
    
    if not has_images:
        print("🚫 Aucune image speech-to-note-frontend à lancer")
        return False
    
    # Get available tags
    available_tags = get_available_tags(image_name)
    
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
        port_input = input("Port à utiliser (défaut: 3000): ").strip()
        
        if not port_input:
            port = 3000
            break
        
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                break
            else:
                print("❌ Le port doit être entre 1 et 65535")
        except ValueError:
            print("❌ Le port doit être un nombre")
    
    # Ask for container name
    print("\n📂 Nom du conteneur")
    default_container_name = f"speech-to-note-frontend-{tag}"
    container_input = input(f"Nom du conteneur (défaut: {default_container_name}): ").strip()
    container_name = container_input if container_input else default_container_name
    
    # Check for existing container
    if not stop_existing_container(container_name):
        print("🚫 Impossible de continuer avec un conteneur existant")
        return False
    
    full_image_name = f"{image_name}:{tag}"
    
    # Confirmation
    print(f"\n📋 Configuration:")
    print(f"   Image: {full_image_name}")
    print(f"   Conteneur: {container_name}")
    print(f"   Port: {port}:80")
    
    confirm = input("\n❓ Confirmer le lancement? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("🚫 Lancement annulé")
        return False
    
    # Run the container
    print(f"🚀 Lancement du conteneur {container_name}...")
    result = subprocess.run([
        "docker", "run", "-d",
        "--name", container_name,
        "-p", f"{port}:80",
        full_image_name
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Conteneur Vue.js {container_name} démarré avec succès!")
        print(f"🌐 Frontend disponible à: http://localhost:{port}")
        print("")
        print("📋 Commandes utiles:")
        print(f"   • Voir les logs: docker logs {container_name}")
        print(f"   • Arrêter: docker stop {container_name}")
        print(f"   • Supprimer: docker rm {container_name}")
        return True
    else:
        print(f"❌ Échec du démarrage du conteneur Vue.js")
        print(f"💥 Erreur: {result.stderr}")
        return False

def main():
    """Main function"""
    print("🚀 Script de lancement de conteneurs Docker pour SpeechToNote")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Choose service
    service_type = choose_service()
    
    print(f"\n✅ Service sélectionné: {service_type.upper()}")
    
    # Run appropriate container
    if service_type == "fastapi":
        success = run_fastapi_container()
    else:  # vuejs
        success = run_vuejs_container()
    
    if not success:
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
    
    input("Press Enter to continue...")
