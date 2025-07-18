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
    print("🏷️ Sélection du/des conteneur(s) à démarrer")
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
    print("  - Saisir UN numéro pour un seul conteneur")
    print("  - Saisir PLUSIEURS numéros séparés par des virgules (ex: 1,3,5)")
    print("  - Saisir des noms de conteneurs séparés par des virgules")
    print("  - Mélanger numéros et noms (ex: 1,mongo-local,3)")
    
    # Get container selection(s)
    while True:
        selection = input("\n🔖 Quel(s) conteneur(s) voulez-vous démarrer? ").strip()
        
        if not selection:
            print("❌ La sélection ne peut pas être vide")
            continue
        
        selected_containers = []
        selections = [s.strip() for s in selection.split(',')]
        
        for sel in selections:
            container_found = None
            
            # Check if it's a number (index)
            if sel.isdigit():
                index = int(sel) - 1
                if 0 <= index < len(containers):
                    container_found = containers[index]
                else:
                    print(f"❌ Numéro {sel} invalide. Choisissez entre 1 et {len(containers)}")
                    break
            else:
                # Check by name or ID
                for container in containers:
                    if (sel.lower() == container['name'].lower() or 
                        sel.lower() == container['id'].lower() or
                        container['id'].startswith(sel.lower())):
                        container_found = container
                        break
                
                if not container_found:
                    print(f"❌ Conteneur '{sel}' non trouvé")
                    break
            
            # Check for duplicates
            if container_found and not any(c['id'] == container_found['id'] for c in selected_containers):
                selected_containers.append(container_found)
            elif container_found:
                print(f"⚠️ Conteneur {container_found['name']} déjà sélectionné, ignoré")
        
        if len(selected_containers) == len(selections):
            break
    
    if not selected_containers:
        print("🚫 Aucun conteneur valide sélectionné")
        sys.exit(0)
    
    # Show selected containers and ask for confirmation
    print(f"\n📋 Conteneurs sélectionnés ({len(selected_containers)}):")
    running_containers = []
    stopped_containers = []
    
    for i, container in enumerate(selected_containers, 1):
        is_running = 'Up' in container['status']
        status_icon = "🟢" if is_running else "🔴"
        action = "redémarrage" if is_running else "démarrage"
        
        print(f"  {i}. {status_icon} {container['name']} - {action}")
        
        if is_running:
            running_containers.append(container)
        else:
            stopped_containers.append(container)
    
    print(f"\n📊 Résumé: {len(stopped_containers)} à démarrer, {len(running_containers)} à redémarrer")
    
    if running_containers:
        print(f"⚠️ {len(running_containers)} conteneur(s) en cours d'exécution seront redémarrés")
    
    confirm = input(f"\n❓ Confirmer le démarrage de {len(selected_containers)} conteneur(s)? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("🚫 Démarrage annulé")
        sys.exit(0)
    
    # Start containers in order
    success_count = 0
    failed_containers = []
    
    print(f"\n🚀 Démarrage de {len(selected_containers)} conteneur(s) en ordre...")
    
    for i, container in enumerate(selected_containers, 1):
        container_id = container['id']
        container_name = container['name']
        is_running = 'Up' in container['status']
        
        print(f"\n[{i}/{len(selected_containers)}] {'🔄' if is_running else '🚀'} {container_name}")
        
        if is_running:
            success = restart_container(container_id, container_name)
        else:
            success = start_container(container_id, container_name)
        
        if success:
            success_count += 1
            # Add small delay between container starts
            if i < len(selected_containers):
                print("⏳ Attente de 2 secondes avant le prochain conteneur...")
                import time
                time.sleep(2)
        else:
            failed_containers.append(container_name)
    
    # Final summary
    print(f"\n{'🎉' if success_count == len(selected_containers) else '⚠️'} Démarrage terminé!")
    print(f"✅ {success_count}/{len(selected_containers)} conteneur(s) démarré(s) avec succès")
    
    if failed_containers:
        print(f"❌ Échecs: {', '.join(failed_containers)}")
        print(f"💡 Vérifiez les logs des conteneurs en échec")
    else:
        print(f"💡 Tous les conteneurs sont maintenant en cours d'exécution")
    
    print(f"\n💡 Commandes utiles:")
    print(f"   docker ps")
    print(f"   docker logs <container_name>")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Démarrage interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)