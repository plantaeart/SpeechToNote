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
    print("🔍 Recherche des images FastAPI existantes...")
    cmd = "docker images speechtonote --format \"table {{.Repository}}\\t{{.Tag}}\\t{{.CreatedAt}}\\t{{.Size}}\""
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        print("\n📦 Images existantes:")
        print(stdout)
        return True
    else:
        print("ℹ️ Aucune image speechtonote trouvée")
        return False

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

def build_image(tag, dockerfile_path, context_path):
    """Build the Docker image"""
    image_name = f"speechtonote:{tag}"
    
    print(f"\n🏗️ Construction de l'image: {image_name}")
    print(f"📂 Contexte: {context_path}")
    print(f"📄 Dockerfile: {dockerfile_path}")
    
    cmd = f'docker build -t {image_name} -f "{dockerfile_path}" "{context_path}"'
    
    print(f"\n🔨 Commande: {cmd}")
    print("⏳ Construction en cours...")
    
    _, stderr, returncode = run_command(cmd)
    
    if returncode == 0:
        print(f"✅ Image {image_name} construite avec succès!")
        
        # Show image info
        print(f"\n📊 Informations sur l'image:")
        info_cmd = f"docker images {image_name} --format \"table {{.Repository}}\\t{{.Tag}}\\t{{.CreatedAt}}\\t{{.Size}}\""
        stdout, _, _ = run_command(info_cmd, capture_output=True)
        if stdout:
            print(stdout)
        
        return True
    else:
        print(f"❌ Erreur lors de la construction: {stderr}")
        return False

def main():
    """Main function"""
    print("🚀 Script de construction d'image Docker pour SpeechToNote API")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    # Show existing images
    get_existing_images()
    
    # Get project paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..", "..")
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
        # Try alternative paths
        alternative_paths = [
            os.path.join(project_root, "backend", "Dockerfile"),
            os.path.join(project_root, "backend", "speech-to-note-backend", "Dockerfile"),
            os.path.join(script_dir, "..", "..", "backend", "Dockerfile")
        ]
        
        print("🔍 Recherche dans d'autres emplacements...")
        for alt_path in alternative_paths:
            alt_path = os.path.abspath(alt_path)
            print(f"   Vérification: {alt_path}")
            if os.path.exists(alt_path):
                print(f"✅ Dockerfile trouvé: {alt_path}")
                dockerfile_path = alt_path
                backend_dir = os.path.dirname(alt_path)
                break
        else:
            print("❌ Aucun Dockerfile trouvé dans les emplacements possibles")
            sys.exit(1)
    
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
        
        # Validate tag (basic validation)
        if any(char in tag for char in [' ', ':', '/', '\\']):
            print("❌ Le tag contient des caractères invalides")
            continue
        
        break
    
    # Confirmation
    print(f"\n📋 Résumé:")
    print(f"   Image: speechtonote:{tag}")
    print(f"   Contexte: {backend_dir}")
    print(f"   Dockerfile: {dockerfile_path}")
    
    confirm = input("\n❓ Confirmer la construction? (y/N): ").strip().lower()

    if confirm not in ['y', 'yes']:
        print("🚫 Construction annulée")
        sys.exit(0)
    
    # Build the image
    success = build_image(tag, dockerfile_path, backend_dir)
    
    if success:
        print(f"\n🎉 Construction terminée avec succès!")
        print(f"💡 Pour tester l'image:")
        print(f"   docker run -p 8000:8000 speechtonote:{tag}")
        print(f"💡 Pour pousser l'image:")
        print(f"   docker tag speechtonote:{tag} your-registry/speechtonote:{tag}")
        print(f"   docker push your-registry/speechtonote:{tag}")
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
