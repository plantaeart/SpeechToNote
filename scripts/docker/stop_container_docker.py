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
    print("🏷️ Sélection du/des conteneur(s) à arrêter")
    print("Conteneurs disponibles:")
    
    for i, container in enumerate(containers, 1):
        status_icon = "🟢" if 'Up' in container['status'] else "🔴"
        print(f"  {i}. {status_icon} {container['name']} ({container['id'][:12]})")
        print(f"     Image: {container['image']}")
        print(f"     Status: {container['status']}")
        print()
    
    print("Options de sélection:")
    print("  - Numéro(s): 1,3,5 ou 1-3 ou 1,2-4")
    print("  - Noms: mon-app,ma-db")
    print("  - 'all' pour arrêter tous les conteneurs")
    print("  - Un seul numéro, nom ou ID")
    
    # Get container selection
    while True:
        selection = input("\n🔖 Quel(s) conteneur(s) voulez-vous arrêter? ").strip()
        
        if not selection:
            print("❌ La sélection ne peut pas être vide")
            continue
        
        selected_containers = []
        
        # Handle 'all' selection
        if selection.lower() == 'all':
            selected_containers = containers
            break
        
        # Handle multiple selections
        if ',' in selection or '-' in selection:
            parts = selection.split(',')
            valid_selection = True
            
            for part in parts:
                part = part.strip()
                
                # Handle range (e.g., "1-3")
                if '-' in part and part.replace('-', '').isdigit():
                    range_parts = part.split('-')
                    if len(range_parts) == 2:
                        try:
                            start = int(range_parts[0])
                            end = int(range_parts[1])
                            for i in range(start, end + 1):
                                if 1 <= i <= len(containers):
                                    container = containers[i - 1]
                                    if container not in selected_containers:
                                        selected_containers.append(container)
                                else:
                                    print(f"❌ Numéro {i} invalide")
                                    valid_selection = False
                                    break
                        except ValueError:
                            print(f"❌ Format de plage invalide: {part}")
                            valid_selection = False
                            break
                    else:
                        print(f"❌ Format de plage invalide: {part}")
                        valid_selection = False
                        break
                
                # Handle single number
                elif part.isdigit():
                    index = int(part) - 1
                    if 0 <= index < len(containers):
                        container = containers[index]
                        if container not in selected_containers:
                            selected_containers.append(container)
                    else:
                        print(f"❌ Numéro {part} invalide")
                        valid_selection = False
                        break
                
                # Handle name or ID
                else:
                    found = False
                    for container in containers:
                        if (part.lower() == container['name'].lower() or 
                            part.lower() == container['id'].lower() or
                            container['id'].startswith(part.lower())):
                            if container not in selected_containers:
                                selected_containers.append(container)
                            found = True
                            break
                    
                    if not found:
                        print(f"❌ Conteneur '{part}' non trouvé")
                        valid_selection = False
                        break
            
            if valid_selection and selected_containers:
                break
            elif not selected_containers:
                print("❌ Aucun conteneur sélectionné")
                continue
        
        # Handle single selection
        else:
            # Check if it's a number (index)
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(containers):
                    selected_containers = [containers[index]]
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
                        selected_containers = [container]
                        break
                
                if selected_containers:
                    break
                else:
                    print(f"❌ Conteneur '{selection}' non trouvé")
                    continue
    
    # Check if any containers are not running
    non_running = [c for c in selected_containers if 'Up' not in c['status']]
    if non_running:
        print(f"\n⚠️ {len(non_running)} conteneur(s) ne sont pas en cours d'exécution:")
        for container in non_running:
            print(f"   - {container['name']}: {container['status']}")
        
        continue_anyway = input("   Continuer quand même? (y/N): ").strip().lower()
        if continue_anyway not in ['y', 'yes']:
            print("🚫 Arrêt annulé")
            sys.exit(0)
    
    # Show summary
    print(f"\n📋 Résumé ({len(selected_containers)} conteneur(s) sélectionné(s)):")
    for i, container in enumerate(selected_containers, 1):
        status_icon = "🟢" if 'Up' in container['status'] else "🔴"
        print(f"  {i}. {status_icon} {container['name']} ({container['id'][:12]})")
        print(f"     Image: {container['image']}")
        print(f"     Status: {container['status']}")
    
    # Final confirmation
    confirm = input(f"\n❓ Confirmer l'arrêt de {len(selected_containers)} conteneur(s)? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("🚫 Arrêt annulé")
        sys.exit(0)
    
    # Ask about stop method
    print("\n🛠️ Méthode d'arrêt:")
    print("1. Arrêt normal (docker stop)")
    print("2. Arrêt forcé (docker kill)")
    print("3. Essayer normal, puis forcé si échec")
    
    while True:
        method_choice = input("\nChoisissez (1/2/3, défaut: 1): ").strip()
        
        if not method_choice or method_choice == "1":
            stop_method = "normal"
            break
        elif method_choice == "2":
            stop_method = "force"
            break
        elif method_choice == "3":
            stop_method = "auto"
            break
        else:
            print("❌ Choisissez 1, 2 ou 3")
    
    # Stop containers
    print(f"\n🚀 Début de l'arrêt de {len(selected_containers)} conteneur(s)")
    print("=" * 60)
    
    successful_stops = []
    failed_stops = []
    
    for i, container in enumerate(selected_containers, 1):
        container_id = container['id']
        container_name = container['name']
        
        print(f"\n[{i}/{len(selected_containers)}] Traitement: {container_name}")
        
        success = False
        
        if stop_method in ["normal", "auto"]:
            success = stop_container(container_id, container_name)
        
        if not success and stop_method in ["force", "auto"]:
            if stop_method == "auto":
                print("   Tentative d'arrêt forcé...")
            success = force_stop_container(container_id, container_name)
        
        if success:
            successful_stops.append(container_name)
        else:
            failed_stops.append(container_name)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 Résumé final")
    
    if successful_stops:
        print(f"\n✅ Conteneurs arrêtés avec succès ({len(successful_stops)}):")
        for name in successful_stops:
            print(f"   - {name}")
    
    if failed_stops:
        print(f"\n❌ Échecs d'arrêt ({len(failed_stops)}):")
        for name in failed_stops:
            print(f"   - {name}")
        
        print(f"\n💡 Pour les échecs, vous pouvez:")
        print(f"   - Vérifier les logs: docker logs <container>")
        print(f"   - Forcer l'arrêt: docker kill <container>")
        print(f"   - Supprimer si nécessaire: docker rm -f <container>")
    
    if successful_stops and not failed_stops:
        print(f"\n🎉 Tous les conteneurs ont été arrêtés avec succès!")
    elif failed_stops:
        print(f"\n⚠️ Arrêt terminé avec {len(failed_stops)} échec(s)")
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
