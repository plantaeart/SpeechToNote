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

def get_container_list():
    """Get container list for selection"""
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

def delete_container(container_id, container_name, force=False):
    """Delete a specific container"""
    force_flag = "-f" if force else ""
    action = "forcée" if force else "normale"
    
    print(f"\n🗑️ Suppression {action} du conteneur: {container_name} ({container_id})")
    
    cmd = f'docker rm {force_flag} {container_id}'
    
    print(f"🔨 Commande: {cmd}")
    print("⏳ Suppression en cours...")
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0:
        print(f"✅ Conteneur {container_name} supprimé avec succès!")
        if stdout:
            print(f"📊 Détails: {stdout}")
        return True
    else:
        print(f"❌ Erreur lors de la suppression: {stderr}")
        if stderr and not force and "cannot remove" in stderr.lower() and "stop the container" in stderr.lower():
            print("💡 Le conteneur est en cours d'exécution. Vous pouvez:")
            print("   - L'arrêter d'abord avec: docker stop")
            print("   - Utiliser la suppression forcée")
        return False

def main():
    """Main function"""
    print("🗑️ Script de suppression de conteneur Docker")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    # Show all containers
    has_containers, _ = get_all_containers()
    
    if not has_containers:
        print("🚫 Aucun conteneur à supprimer")
        sys.exit(0)
    
    # Get container list for selection
    containers = get_container_list()
    
    if not containers:
        print("🚫 Aucun conteneur disponible")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("🏷️ Sélection du conteneur à supprimer")
    print("Conteneurs disponibles:")
    
    for i, container in enumerate(containers, 1):
        if 'Up' in container['status']:
            status_icon = "🟢"
        elif 'Exited' in container['status']:
            status_icon = "🔴"
        else:
            status_icon = "⚪"
            
        print(f"  {i}. {status_icon} {container['name']} ({container['id'][:12]})")
        print(f"     Image: {container['image']}")
        print(f"     Status: {container['status']}")
        print()
    
    # Get container selection
    while True:
        try:
            selection = input(f"\n🔖 Quel conteneur voulez-vous supprimer? (1-{len(containers)}): ").strip()
            
            if not selection:
                print("❌ Veuillez saisir un numéro")
                continue
            
            index = int(selection) - 1
            if 0 <= index < len(containers):
                selected_container = containers[index]
                break
            else:
                print(f"❌ Numéro invalide. Choisissez entre 1 et {len(containers)}")
                continue
                
        except ValueError:
            print("❌ Veuillez saisir un numéro valide")
            continue
    
    container_id = selected_container['id']
    container_name = selected_container['name']
    container_status = selected_container['status']
    is_running = 'Up' in container_status
    
    # Show container details
    print(f"\n📋 Conteneur sélectionné:")
    print(f"   Nom: {container_name}")
    print(f"   ID: {container_id}")
    print(f"   Image: {selected_container['image']}")
    print(f"   Status: {container_status}")
    
    # Warning for running containers
    if is_running:
        print(f"\n⚠️ ATTENTION: Le conteneur {container_name} est en cours d'exécution!")
        print("Options de suppression:")
        print("1. Suppression normale (échouera si le conteneur est en cours)")
        print("2. Suppression forcée (arrête et supprime le conteneur)")
        print("3. Annuler")
        
        while True:
            option = input("\nChoisissez une option (1/2/3): ").strip()
            
            if option == "1":
                force = False
                break
            elif option == "2":
                force = True
                break
            elif option == "3":
                print("🚫 Suppression annulée")
                sys.exit(0)
            else:
                print("❌ Choisissez 1, 2 ou 3")
    else:
        force = False
    
    # Final confirmation
    action_type = "forcée" if force else "normale"
    confirm = input(f"\n❓ Confirmer la suppression {action_type} de '{container_name}'? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("🚫 Suppression annulée")
        sys.exit(0)
    
    # Delete the container
    success = delete_container(container_id, container_name, force)
    
    if success:
        print(f"\n🎉 Suppression terminée avec succès!")
        print(f"💡 Le conteneur {container_name} a été supprimé")
        
        # Show remaining containers
        print(f"\n📦 Conteneurs restants:")
        remaining_cmd = 'docker ps -a --format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}"'
        stdout, _, _ = run_command(remaining_cmd, capture_output=True)
        if stdout:
            print(stdout)
        else:
            print("ℹ️ Aucun conteneur restant")
    else:
        print(f"\n💥 Échec de la suppression")
        if not force and is_running:
            print(f"💡 Conseils:")
            print(f"   - Arrêtez d'abord le conteneur: docker stop {container_name}")
            print(f"   - Ou relancez ce script et choisissez la suppression forcée")
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
