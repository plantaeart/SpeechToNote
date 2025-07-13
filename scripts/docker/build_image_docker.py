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
    print("🎯 Choix du service à construire")
    print("=" * 40)
    print("1. FastAPI (Backend)")
    print("2. Vue.js (Frontend)")
    print("3. Quitter")
    
    while True:
        choice = input("\n🔖 Quel service voulez-vous construire? (1-3): ").strip()
        
        if choice == "1":
            return "fastapi"
        elif choice == "2":
            return "vuejs"
        elif choice == "3":
            print("👋 Au revoir!")
            sys.exit(0)
        else:
            print("❌ Choix invalide. Veuillez saisir 1, 2 ou 3.")

def build_fastapi_image():
    """Build FastAPI Docker image"""
    print("\n🚀 Construction de l'image Docker FastAPI pour SpeechToNote")
    print("=" * 60)
    
    image_name = "speechtonote-backend"
    
    # Show existing images
    get_existing_images(image_name)
    
    # Get project paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..")
    backend_dir = os.path.join(project_root, "backend")
    dockerfile_path = os.path.join(backend_dir, "Dockerfile")
    
    # Normalize paths
    project_root = os.path.abspath(project_root)
    backend_dir = os.path.abspath(backend_dir)
    dockerfile_path = os.path.abspath(dockerfile_path)
    
    print(f"\n📁 Chemin du projet: {project_root}")
    print(f"📁 Chemin backend: {backend_dir}")
    print(f"📄 Dockerfile: {dockerfile_path}")
    
    # Check if Dockerfile exists
    if not os.path.exists(dockerfile_path):
        print(f"❌ Dockerfile introuvable: {dockerfile_path}")
        return False
    
    print("\n" + "=" * 60)
    
    # Ask for tag
    print("🏷️ Gestion des tags")
    print("Suggestions:")
    print("  - latest (dernière version)")
    print("  - v1.0.0 (version spécifique)")
    print("  - dev (version de développement)")
    print(f"  - {datetime.now().strftime('%Y%m%d')} (date du jour)")
    
    while True:
        tag = input("\n🔖 Quel tag voulez-vous utiliser? ").strip()
        
        if not tag:
            print("❌ Le tag ne peut pas être vide")
            continue
        
        # Validate tag
        if any(char in tag for char in [' ', ':', '/', '\\']):
            print("❌ Le tag contient des caractères invalides")
            continue
        
        break
    
    full_image_name = f"{image_name}:{tag}"
    
    # Confirmation
    print(f"\n📋 Résumé:")
    print(f"   Image: {full_image_name}")
    print(f"   Contexte: {backend_dir}")
    print(f"   Dockerfile: {dockerfile_path}")
    
    confirm = input("\n❓ Confirmer la construction? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("🚫 Construction annulée")
        return False
    
    # Build the image
    print(f"\n🔨 Construction de l'image: {full_image_name}")
    print("⏳ Construction en cours...")
    
    cmd = f'docker build -t {full_image_name} -f "{dockerfile_path}" "{backend_dir}"'
    
    _, stderr, returncode = run_command(cmd)
    
    if returncode == 0:
        print(f"✅ Image {full_image_name} construite avec succès!")
        
        # Ask if user wants to run the image
        run_container = input("\n❓ Voulez-vous lancer cette image dans un conteneur maintenant? (y/N): ").strip().lower()
        
        if run_container in ['y', 'yes']:
            return run_fastapi_image_now(image_name, tag)
        
        return True
    else:
        print(f"❌ Erreur lors de la construction: {stderr}")
        return False

def build_vuejs_image():
    """Build Vue.js Docker image"""
    print("\n🚀 Construction de l'image Docker Vue.js pour SpeechToNote")
    print("=" * 60)
    
    image_name = "speechtonote-frontend"
    
    # Show existing images
    get_existing_images(image_name)
    
    # Get project paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..")
    frontend_dir = os.path.join(project_root, "frontend")
    dockerfile_path = os.path.join(frontend_dir, "Dockerfile")
    
    # Normalize paths
    project_root = os.path.abspath(project_root)
    frontend_dir = os.path.abspath(frontend_dir)
    dockerfile_path = os.path.abspath(dockerfile_path)
    
    print(f"\n📁 Chemin du projet: {project_root}")
    print(f"📁 Chemin frontend: {frontend_dir}")
    print(f"📄 Dockerfile: {dockerfile_path}")
    
    # Check if Dockerfile exists
    if not os.path.exists(dockerfile_path):
        print(f"❌ Dockerfile introuvable: {dockerfile_path}")
        return False
    
    print("\n" + "=" * 60)
    
    # Ask for tag
    print("🏷️ Gestion des tags")
    print("Suggestions:")
    print("  - latest (dernière version)")
    print("  - v1.0.0 (version spécifique)")
    print("  - dev (version de développement)")
    print(f"  - {datetime.now().strftime('%Y%m%d')} (date du jour)")
    
    while True:
        tag = input("\n🔖 Quel tag voulez-vous utiliser? ").strip()
        
        if not tag:
            print("❌ Le tag ne peut pas être vide")
            continue
        
        # Validate tag
        if any(char in tag for char in [' ', ':', '/', '\\']):
            print("❌ Le tag contient des caractères invalides")
            continue
        
        break
    
    full_image_name = f"{image_name}:{tag}"
    
    # Confirmation
    print(f"\n📋 Résumé:")
    print(f"   Image: {full_image_name}")
    print(f"   Contexte: {frontend_dir}")
    print(f"   Dockerfile: {dockerfile_path}")
    
    confirm = input("\n❓ Confirmer la construction? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("🚫 Construction annulée")
        return False
    
    # Build the image
    print(f"\n🔨 Construction de l'image: {full_image_name}")
    print("⏳ Construction en cours...")
    
    cmd = f'docker build -t {full_image_name} -f "{dockerfile_path}" "{frontend_dir}"'
    
    _, stderr, returncode = run_command(cmd)
    
    if returncode == 0:
        print(f"✅ Image {full_image_name} construite avec succès!")
        
        # Ask if user wants to run the image
        run_container = input("\n❓ Voulez-vous lancer cette image dans un conteneur maintenant? (y/N): ").strip().lower()
        
        if run_container in ['y', 'yes']:
            return run_vuejs_image_now(image_name, tag)
        
        return True
    else:
        print(f"❌ Erreur lors de la construction: {stderr}")
        return False

def run_fastapi_image_now(image_name, tag):
    """Run FastAPI image immediately after build"""
    print("\n🚀 Configuration du conteneur FastAPI")
    
    # Ask for port
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
    default_container_name = f"speechtonote-backend-{tag}"
    container_input = input(f"Nom du conteneur (défaut: {default_container_name}): ").strip()
    container_name = container_input if container_input else default_container_name
    
    # Stop existing container if exists
    check_cmd = f"docker ps -a --filter name=^/{container_name}$ --format \"{{{{.Names}}}}\""
    stdout, _, _ = run_command(check_cmd, capture_output=True)
    
    if stdout and stdout.strip():
        print(f"🛑 Arrêt et suppression du conteneur existant {container_name}...")
        run_command(f"docker stop {container_name}", capture_output=True)
        run_command(f"docker rm {container_name}", capture_output=True)
    
    full_image_name = f"{image_name}:{tag}"
    
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
        return True
    else:
        print(f"❌ Échec du démarrage du conteneur")
        print(f"💥 Erreur: {result.stderr}")
        return False

def run_vuejs_image_now(image_name, tag):
    """Run Vue.js image immediately after build"""
    print("\n🚀 Configuration du conteneur Vue.js")
    
    # Ask for port
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
    default_container_name = f"speech-to-note-frontend-{tag}"
    container_input = input(f"Nom du conteneur (défaut: {default_container_name}): ").strip()
    container_name = container_input if container_input else default_container_name
    
    # Stop existing container if exists
    check_cmd = f"docker ps -a --filter name=^/{container_name}$ --format \"{{{{.Names}}}}\""
    stdout, _, _ = run_command(check_cmd, capture_output=True)
    
    if stdout and stdout.strip():
        print(f"🛑 Arrêt et suppression du conteneur existant {container_name}...")
        run_command(f"docker stop {container_name}", capture_output=True)
        run_command(f"docker rm {container_name}", capture_output=True)
    
    full_image_name = f"{image_name}:{tag}"
    
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
        return True
    else:
        print(f"❌ Échec du démarrage du conteneur")
        print(f"💥 Erreur: {result.stderr}")
        return False

def main():
    """Main function"""
    print("🚀 Script de construction d'images Docker pour SpeechToNote")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Choose service
    service_type = choose_service()
    
    print(f"\n✅ Service sélectionné: {service_type.upper()}")
    
    # Build appropriate image
    if service_type == "fastapi":
        success = build_fastapi_image()
    else:  # vuejs
        success = build_vuejs_image()
    
    if success:
        print(f"\n🎉 Construction terminée avec succès!")
    else:
        print(f"\n💥 Échec de la construction")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Construction interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)
    
    input("Press Enter to continue...")
