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

def get_existing_images(image_name):
    """Get list of existing images"""
    print(f"🔍 Recherche des images {image_name} existantes...")
    cmd = f"docker images {image_name} --format \"table {{{{.Repository}}}}\\t{{{{.Tag}}}}\\t{{{{.CreatedAt}}}}\\t{{{{.Size}}}}\""
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        print("\n📦 Images existantes:")
        print(stdout)
        return True, stdout
    else:
        print(f"ℹ️ Aucune image {image_name} trouvée")
        return False, ""

def get_available_tags(image_name):
    """Get list of available tags for images"""
    cmd = f"docker images {image_name} --format \"{{{{.Tag}}}}\""
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        tags = [tag.strip() for tag in stdout.split('\n') if tag.strip()]
        return tags
    else:
        return []

def get_containers_using_image(image_name):
    """Get list of containers using the specified image"""
    cmd = f'docker ps -a --filter ancestor={image_name} --format "{{{{.ID}}}}\\t{{{{.Names}}}}\\t{{{{.Status}}}}"'
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        containers = []
        for line in stdout.split('\n'):
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    containers.append({
                        'id': parts[0],
                        'name': parts[1],
                        'status': parts[2]
                    })
        return containers
    return []

def stop_and_remove_containers(containers):
    """Stop and remove containers"""
    success = True
    
    for container in containers:
        container_id = container['id']
        container_name = container['name']
        container_status = container['status']
        
        print(f"📦 Conteneur trouvé: {container_name} ({container_id}) - {container_status}")
        
        # Stop container if it's running
        if 'Up' in container_status:
            print(f"🛑 Arrêt du conteneur {container_name}...")
            stop_cmd = f'docker stop {container_id}'
            stdout, stderr, returncode = run_command(stop_cmd, capture_output=True)
            
            if returncode == 0:
                print(f"✅ Conteneur {container_name} arrêté")
            else:
                print(f"❌ Erreur lors de l'arrêt: {stderr}")
                success = False
                continue
        
        # Remove container
        print(f"🗑️ Suppression du conteneur {container_name}...")
        rm_cmd = f'docker rm {container_id}'
        stdout, stderr, returncode = run_command(rm_cmd, capture_output=True)
        
        if returncode == 0:
            print(f"✅ Conteneur {container_name} supprimé")
        else:
            print(f"❌ Erreur lors de la suppression: {stderr}")
            success = False
    
    return success

def delete_image(image_name, tag):
    """Delete the Docker image and associated containers"""
    full_image_name = f"{image_name}:{tag}"
    
    print(f"\n🗑️ Suppression de l'image: {full_image_name}")
    
    # First, check for containers using this image
    print("🔍 Recherche des conteneurs utilisant cette image...")
    containers = get_containers_using_image(full_image_name)
    
    if containers:
        print(f"⚠️ Trouvé {len(containers)} conteneur(s) utilisant cette image:")
        for container in containers:
            print(f"   - {container['name']} ({container['id']}) - {container['status']}")
        
        confirm_containers = input("\n❓ Arrêter et supprimer ces conteneurs? (y/N): ").strip().lower()
        
        if confirm_containers in ['y', 'yes']:
            print("\n🔧 Suppression des conteneurs...")
            if not stop_and_remove_containers(containers):
                print("❌ Erreur lors de la suppression des conteneurs")
                return False
        else:
            print("🚫 Suppression annulée - impossible de supprimer l'image avec des conteneurs actifs")
            return False
    else:
        print("✅ Aucun conteneur utilisant cette image")
    
    # Now delete the image
    print(f"\n🗑️ Suppression de l'image: {full_image_name}")
    cmd = f'docker rmi {full_image_name}'
    
    print(f"\n🔨 Commande: {cmd}")
    print("⏳ Suppression en cours...")
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0:
        print(f"✅ Image {full_image_name} supprimée avec succès!")
        if stdout:
            print(f"📊 Détails: {stdout}")
        return True
    else:
        print(f"❌ Erreur lors de la suppression: {stderr}")
        return False

def force_delete_image(image_name, tag):
    """Force delete the Docker image and associated containers"""
    full_image_name = f"{image_name}:{tag}"
    
    print(f"\n🗑️ Suppression forcée de l'image: {full_image_name}")
    
    # Force remove containers first
    print("🔍 Recherche des conteneurs utilisant cette image...")
    containers = get_containers_using_image(full_image_name)
    
    if containers:
        print(f"⚠️ Suppression forcée de {len(containers)} conteneur(s):")
        for container in containers:
            container_id = container['id']
            container_name = container['name']
            print(f"🗑️ Suppression forcée du conteneur {container_name}...")
            
            force_rm_cmd = f'docker rm -f {container_id}'
            stdout, stderr, returncode = run_command(force_rm_cmd, capture_output=True)
            
            if returncode == 0:
                print(f"✅ Conteneur {container_name} supprimé (forcé)")
            else:
                print(f"❌ Erreur lors de la suppression forcée: {stderr}")
    
    # Force delete the image
    cmd = f'docker rmi -f {full_image_name}'
    
    print(f"\n🔨 Commande: {cmd}")
    print("⏳ Suppression forcée en cours...")
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0:
        print(f"✅ Image {full_image_name} supprimée avec succès (forcée)!")
        if stdout:
            print(f"📊 Détails: {stdout}")
        return True
    else:
        print(f"❌ Erreur lors de la suppression forcée: {stderr}")
        return False

def choose_service():
    """Let user choose between FastAPI and Vue.js"""
    print("🎯 Choix du service à supprimer")
    print("=" * 40)
    print("1. FastAPI (Backend)")
    print("2. Vue.js (Frontend)")
    print("3. Quitter")
    
    while True:
        choice = input("\n🔖 Quel service voulez-vous supprimer? (1-3): ").strip()
        
        if choice == "1":
            return "fastapi", "speechtonote"
        elif choice == "2":
            return "vuejs", "speech-to-note-frontend"
        elif choice == "3":
            print("👋 Au revoir!")
            sys.exit(0)
        else:
            print("❌ Choix invalide. Veuillez saisir 1, 2 ou 3.")

def delete_service_images(service_type, image_name):
    """Delete images for a specific service"""
    print(f"\n🗑️ Script de suppression d'images Docker {service_type.upper()} pour SpeechToNote")
    print("=" * 60)
    
    # Show existing images
    has_images, images_output = get_existing_images(image_name)
    
    if not has_images:
        print(f"🚫 Aucune image {image_name} à supprimer")
        return False
    
    # Get available tags
    available_tags = get_available_tags(image_name)
    
    print("\n" + "=" * 60)
    
    # Ask for tag
    print("🏷️ Suppression par tag")
    if available_tags:
        print("Tags disponibles:")
        for i, tag in enumerate(available_tags, 1):
            print(f"  {i}. {tag}")
        print("\nVous pouvez:")
        print("  - Saisir le nom du tag directement")
        print("  - Saisir le numéro correspondant")
    
    while True:
        tag_input = input("\n🔖 Quel tag voulez-vous supprimer? ").strip()
        
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
    
    # Confirmation
    print(f"\n📋 Résumé:")
    print(f"   Image à supprimer: {image_name}:{tag}")
    print(f"   ⚠️ Les conteneurs associés seront également supprimés")
    
    confirm = input("\n❓ Confirmer la suppression? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("🚫 Suppression annulée")
        return False
    
    # Try to delete the image (with containers)
    success = delete_image(image_name, tag)
    
    if not success:
        # Ask if user wants to force delete
        force_confirm = input("\n❓ Voulez-vous forcer la suppression? (y/N): ").strip().lower()
        
        if force_confirm in ['y', 'yes']:
            success = force_delete_image(image_name, tag)
    
    if success:
        print(f"\n🎉 Suppression terminée avec succès!")
        print(f"\n📦 Images restantes:")
        # Show remaining images
        has_remaining, _ = get_existing_images(image_name)
        if not has_remaining:
            print(f"ℹ️ Aucune image {image_name} restante")
        return True
    else:
        print(f"\n💥 Échec de la suppression")
        print(f"💡 Conseils:")
        print(f"   - Vérifiez les permissions Docker")
        print(f"   - Essayez la suppression forcée")
        print(f"   - Utilisez 'docker system prune' pour nettoyer complètement")
        return False

def main():
    """Main function"""
    print("🗑️ Script de suppression d'images Docker pour SpeechToNote")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Choose service
    service_type, image_name = choose_service()
    
    print(f"\n✅ Service sélectionné: {service_type.upper()}")
    
    # Delete images for the selected service
    success = delete_service_images(service_type, image_name)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Suppression interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)
    
    input("Press Enter to continue...")
