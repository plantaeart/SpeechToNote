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

def get_stopped_containers():
    """Get list of stopped containers"""
    print("🔍 Recherche des conteneurs arrêtés...")
    cmd = 'docker ps -a --filter "status=exited" --format "table {{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"'
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0 and stdout:
        print("\n🔴 Conteneurs arrêtés:")
        print(stdout)
        return True, stdout
    else:
        print("ℹ️ Aucun conteneur arrêté")
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

def get_container_list(stopped_only=True):
    """Get container list for selection"""
    if stopped_only:
        cmd = 'docker ps -a --filter "status=exited" --format "{{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}"'
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

def start_container(container_id, container_name):
    """Start a specific container"""
    print(f"\n🚀 Démarrage du conteneur: {container_name} ({container_id})")
    
    cmd = f'docker start {container_id}'
    
    print(f"🔨 Commande: {cmd}")
    print("⏳ Démarrage en cours...")
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0:
        print(f"✅ Conteneur {container_name} démarré avec succès!")
        if stdout:
            print(f"📊 Détails: {stdout}")
        
        # Show logs briefly to confirm it's running
        print(f"\n📋 Vérification du statut...")
        status_cmd = f'docker ps --filter "id={container_id}" --format "{{{{.Status}}}}"'
        status_out, _, _ = run_command(status_cmd, capture_output=True)
        if status_out:
            print(f"📊 Statut actuel: {status_out}")
        
        return True
    else:
        print(f"❌ Erreur lors du démarrage: {stderr}")
        return False

def restart_container(container_id, container_name):
    """Restart a specific container"""
    print(f"\n🔄 Redémarrage du conteneur: {container_name} ({container_id})")
    
    cmd = f'docker restart {container_id}'
    
    print(f"🔨 Commande: {cmd}")
    print("⏳ Redémarrage en cours...")
    
    stdout, stderr, returncode = run_command(cmd, capture_output=True)
    
    if returncode == 0:
        print(f"✅ Conteneur {container_name} redémarré avec succès!")
        if stdout:
            print(f"📊 Détails: {stdout}")
        return True
    else:
        print(f"❌ Erreur lors du redémarrage: {stderr}")
        return False

def main():
    """Main function"""
    print("🚀 Script de démarrage de conteneur Docker")
    print("=" * 60)
    
    # Check Docker status
    if not get_docker_status():
        sys.exit(1)
    
    # Ask what to show
    print("\n" + "=" * 60)
    print("🔍 Type de conteneurs à afficher:")
    print("1. Conteneurs arrêtés uniquement")
    print("2. Tous les conteneurs (en cours et arrêtés)")
    
    while True:
        choice = input("\nChoisissez (1/2, défaut: 1): ").strip()
        
        if not choice or choice == "1":
            stopped_only = True
            break
        elif choice == "2":
            stopped_only = False
            break
        else:
            print("❌ Choisissez 1 ou 2")
    
    # Show containers
    if stopped_only:
        has_containers, _ = get_stopped_containers()
    else:
        has_containers, _ = get_all_containers()
    
    if not has_containers:
        print("🚫 Aucun conteneur à démarrer")
        sys.exit(0)
    
    # Get container list for selection
    containers = get_container_list(stopped_only)
    
    if not containers:
        print("🚫 Aucun conteneur disponible")
        sys.exit(0)
    
    # Filter stopped containers if needed
    if stopped_only:
        containers = [c for c in containers if 'Exited' in c['status'] or 'Created' in c['status']]
        
        if not containers:
            print("🚫 Aucun conteneur arrêté")
            sys.exit(0)
    
    print("\n" + "=" * 60)
    print("🏷️ Sélection du conteneur à démarrer")
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
    
    print("Vous pouvez:")
    print("  - Saisir le numéro correspondant")
    print("  - Saisir le nom du conteneur directement")
    print("  - Saisir l'ID du conteneur")
    
    # Get container selection
    while True:
        selection = input("\n🔖 Quel conteneur voulez-vous démarrer? ").strip()
        
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
    
    # Check if container is already running
    is_running = 'Up' in container_status
    
    # Ask for action if container is already running
    if is_running:
        print(f"⚠️ Le conteneur {container_name} est déjà en cours d'exécution")
        print(f"   Status actuel: {container_status}")
        print("🔧 Actions disponibles:")
        print("1. Redémarrer le conteneur")
        print("2. Annuler")
        
        while True:
            action_choice = input("\nChoisissez (1/2): ").strip()
            
            if action_choice == "1":
                action = "restart"
                break
            elif action_choice == "2":
                print("🚫 Démarrage annulé")
                sys.exit(0)
            else:
                print("❌ Choisissez 1 ou 2")
    else:
        action = "start"
    
    # Confirmation
    print(f"\n📋 Résumé:")
    print(f"   Conteneur: {container_name}")
    print(f"   ID: {container_id}")
    print(f"   Image: {selected_container['image']}")
    print(f"   Status: {container_status}")
    print(f"   Action: {'Redémarrage' if action == 'restart' else 'Démarrage'}")
    
    confirm = input(f"\n❓ Confirmer le {'redémarrage' if action == 'restart' else 'démarrage'}? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("🚫 Action annulée")
        sys.exit(0)
    
    # Execute the action
    if action == "restart":
        success = restart_container(container_id, container_name)
    else:
        success = start_container(container_id, container_name)
    
    if success:
        print(f"\n🎉 {'Redémarrage' if action == 'restart' else 'Démarrage'} terminé avec succès!")
        print(f"💡 Commandes utiles:")
        print(f"   docker logs {container_name}")
        print(f"   docker logs -f {container_name}")
        print(f"   docker stop {container_name}")
        print(f"   docker exec -it {container_name} /bin/bash")
        
        # Show ports if container exposes any
        ports_cmd = f'docker port {container_id}'
        ports_out, _, _ = run_command(ports_cmd, capture_output=True)
        if ports_out:
            print(f"🌐 Ports exposés:")
            for line in ports_out.split('\n'):
                if line.strip():
                    print(f"   {line}")
    else:
        print(f"\n💥 Échec du {'redémarrage' if action == 'restart' else 'démarrage'}")
        print(f"💡 Conseils:")
        print(f"   - Vérifiez que le conteneur existe")
        print(f"   - Vérifiez les logs: docker logs {container_name}")
        print(f"   - Vérifiez la configuration Docker")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Démarrage interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)