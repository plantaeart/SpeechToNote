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

def get_running_containers():
    """Get list of running containers"""
    print("🔍 Recherche des conteneurs en cours d'exécution...")
    cmd = 'docker ps --format "table {{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"'
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        print("\n🚀 Conteneurs en cours d'exécution:")
        print(stdout)
        return True, stdout
    else:
        print("ℹ️ Aucun conteneur en cours d'exécution")
        return False, ""

def get_all_containers():
    """Get list of all containers (running and stopped)"""
    print("🔍 Recherche de tous les conteneurs...")
    cmd = 'docker ps -a --format "table {{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"'
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        print("\n📦 Tous les conteneurs:")
        print(stdout)
        return True, stdout
    else:
        print("ℹ️ Aucun conteneur trouvé")
        return False, ""

def get_container_list(running_only=True):
    """Get container list for selection"""
    if running_only:
        cmd = 'docker ps --format "{{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}"'
    else:
        cmd = 'docker ps -a --format "{{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}"'
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        containers = []
        for line in stdout.split('\n'):
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    containers.append({
                        'id': parts[0],
                        'name': parts[1],
                        'image': parts[2],
                        'status': parts[3]
                    })
        return containers
    return []

def stop_container(container_id, container_name):
    """Stop a specific container"""
    print(f"\n🛑 Arrêt du conteneur: {container_name} ({container_id})")
    
    cmd = f'docker stop {container_id}'
    
    print(f"🔨 Commande: {cmd}")
    print("⏳ Arrêt en cours...")
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0:
        print(f"✅ Conteneur {container_name} arrêté avec succès!")
        if stdout:
            print(f"📊 Détails: {stdout}")
        return True
    else:
        print(f"❌ Erreur lors de l'arrêt: {stderr}")
        return False

def force_stop_container(container_id, container_name):
    """Force stop a specific container"""
    print(f"\n🛑 Arrêt forcé du conteneur: {container_name} ({container_id})")
    
    cmd = f'docker kill {container_id}'
    
    print(f"🔨 Commande: {cmd}")
    print("⏳ Arrêt forcé en cours...")
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0:
        print(f"✅ Conteneur {container_name} arrêté avec succès (forcé)!")
        if stdout:
            print(f"📊 Détails: {stdout}")
        return True
    else:
        print(f"❌ Erreur lors de l'arrêt forcé: {stderr}")
        return False

def main():
    """Main function"""
    print("🛑 Script d'arrêt de conteneur Docker")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    # Ask what to show
    print("\n" + "=" * 60)
    print("🔍 Type de conteneurs à afficher:")
    print("1. Conteneurs en cours d'exécution uniquement")
    print("2. Tous les conteneurs (en cours et arrêtés)")
    
    while True:
        choice = input("\nChoisissez (1/2, défaut: 1): ").strip()
        
        if not choice or choice == "1":
            running_only = True
            break
        elif choice == "2":
            running_only = False
            break
        else:
            print("❌ Choisissez 1 ou 2")
    
    # Show containers
    if running_only:
        has_containers, _ = get_running_containers()
    else:
        has_containers, _ = get_all_containers()
    
    if not has_containers:
        print("🚫 Aucun conteneur à arrêter")
        sys.exit(0)
    
    # Get container list for selection
    containers = get_container_list(running_only)
    
    if not containers:
        print("🚫 Aucun conteneur disponible")
        sys.exit(0)
    
    # Filter running containers if needed
    if running_only:
        containers = [c for c in containers if 'Up' in c['status']]
        
        if not containers:
            print("🚫 Aucun conteneur en cours d'exécution")
            sys.exit(0)
    
    print("\n" + "=" * 60)
    print("🏷️ Sélection du conteneur à arrêter")
    print("Conteneurs disponibles:")
    
    for i, container in enumerate(containers, 1):
        status_icon = "🟢" if 'Up' in container['status'] else "🔴"
        print(f"  {i}. {status_icon} {container['name']} ({container['id'][:12]})")
        print(f"     Image: {container['image']}")
        print(f"     Status: {container['status']}")
        print()
    
    print("Vous pouvez:")
    print("  - Saisir le numéro correspondant")
    print("  - Saisir le nom du conteneur directement")
    print("  - Saisir l'ID du conteneur")
    
    # Get container selection
    while True:
        selection = input("\n🔖 Quel conteneur voulez-vous arrêter? ").strip()
        
        if not selection:
            print("❌ La sélection ne peut pas être vide")
            continue
        
        selected_container = None
        
        # Check if it's a number (index)
        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(containers):
                selected_container = containers[index]
                break
            else:
                print(f"❌ Numéro invalide. Choisissez entre 1 et {len(containers)}")
                continue
        else:
            # Check by name or ID
            for container in containers:
                if (selection.lower() == container['name'].lower() or 
                    selection.lower() == container['id'].lower() or
                    container['id'].startswith(selection.lower())):
                    selected_container = container
                    break
            
            if selected_container:
                break
            else:
                print(f"❌ Conteneur '{selection}' non trouvé")
                continue
    
    container_id = selected_container['id']
    container_name = selected_container['name']
    container_status = selected_container['status']
    
    # Check if container is running
    if 'Up' not in container_status:
        print(f"⚠️ Le conteneur {container_name} n'est pas en cours d'exécution")
        print(f"   Status actuel: {container_status}")
        
        continue_anyway = input("   Continuer quand même? (y/N): ").strip().lower()
        if continue_anyway not in ['y', 'yes']:
            print("🚫 Arrêt annulé")
            sys.exit(0)
    
    # Confirmation
    print(f"\n📋 Résumé:")
    print(f"   Conteneur: {container_name}")
    print(f"   ID: {container_id}")
    print(f"   Image: {selected_container['image']}")
    print(f"   Status: {container_status}")
    
    confirm = input("\n❓ Confirmer l'arrêt? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("🚫 Arrêt annulé")
        sys.exit(0)
    
    # Try to stop the container
    success = stop_container(container_id, container_name)
    
    if not success:
        # Ask if user wants to force stop
        force_confirm = input("\n❓ Voulez-vous forcer l'arrêt? (y/N): ").strip().lower()
        
        if force_confirm in ['y', 'yes']:
            success = force_stop_container(container_id, container_name)
    
    if success:
        print(f"\n🎉 Arrêt terminé avec succès!")
        print(f"💡 Commandes utiles:")
        print(f"   docker start {container_name}")
        print(f"   docker restart {container_name}")
        print(f"   docker logs {container_name}")
        print(f"   docker rm {container_name}")
    else:
        print(f"\n💥 Échec de l'arrêt")
        print(f"💡 Conseils:")
        print(f"   - Vérifiez que le conteneur existe")
        print(f"   - Essayez l'arrêt forcé")
        print(f"   - Utilisez 'docker ps -a' pour voir l'état")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)
