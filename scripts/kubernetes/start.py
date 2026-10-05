import subprocess
import os
import shutil
import sys
import time

def get_host_data_dir():
    """Host directory bind-mounted into the kind node (see manifests/kind-config.yaml)."""
    override = os.getenv("SPEECHTONOTE_DATA_DIR")
    if override:
        return override
    if sys.platform == "win32":
        return os.path.join(os.environ.get("TEMP", r"C:\temp"), "speechtonote-mongo-data")
    return "/tmp/speechtonote-mongo-data"

def ask_tag(service):
    tag = input(f"Entrez le tag Docker pour {service} (par défaut: latest) : ").strip()
    return tag if tag else "latest"

def image_exists(image_name):
    """Check if Docker image exists locally"""
    result = subprocess.run(["docker", "images", "-q", image_name], capture_output=True, text=True)
    return bool(result.stdout.strip())

def wait_for_deployment_ready(deployment_name, timeout=300):
    """Wait for a deployment to be ready"""
    print(f"Attente que le déploiement {deployment_name} soit prêt...")
    start_time = time.time()
    spinner = ['|', '/', '-', '\\']
    i = 0
    
    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                ["kubectl", "get", "deployment", deployment_name, "-o", "jsonpath={.status.readyReplicas}"],
                capture_output=True, text=True, check=True
            )
            ready_replicas = result.stdout.strip()
            if ready_replicas and int(ready_replicas) > 0:
                print(f"\n✓ Déploiement {deployment_name} prêt!")
                return True
        except (subprocess.CalledProcessError, OSError):
            # Not ready yet; the deployment may not exist or kubectl may fail.
            pass
        
        print(f"\r{spinner[i % len(spinner)]} Attente...", end='', flush=True)
        i += 1
        time.sleep(1)
    
    print(f"\n✗ Timeout: {deployment_name} n'est pas prêt après {timeout}s")
    return False

def deploy_in_order(manifests_path):
    """Deploy services in dependency order"""
    
    # 1. Deploy MongoDB storage first
    print("1. Déploiement du stockage MongoDB...")
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "local-storage.yaml")], check=True)
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "mongo-pv.yaml")], check=True)
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "mongo-pvc.yaml")], check=True)
    
    # 2. Deploy MongoDB
    print("2. Déploiement de MongoDB...")
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "mongo-deployment.yaml")], check=True)
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "mongo-service.yaml")], check=True)
    
    if not wait_for_deployment_ready("mongo"):
        return False
    
    # 3. Deploy FastAPI (depends on MongoDB)
    print("3. Déploiement de FastAPI...")
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "fastapi-deployment.yaml")], check=True)
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "fastapi-service.yaml")], check=True)
    
    if not wait_for_deployment_ready("fastapi"):
        return False
    
    # 4. Deploy Vue.js frontend (depends on FastAPI)
    print("4. Déploiement de Vue.js...")
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "vue-deployment.yaml")], check=True)
    subprocess.run(["kubectl", "apply", "-f", os.path.join(manifests_path, "vue-service.yaml")], check=True)
    
    if not wait_for_deployment_ready("vue"):
        return False
    
    return True

def require_binaries(*names):
    """Fail early with a clear message when a required tool is missing.

    Without this, a missing `kind` surfaces as a bare FileNotFoundError
    traceback part-way through a deployment.
    """
    missing = []
    for name in names:
        if shutil.which(name) is None:
            missing.append(name)

    if missing:
        print("❌ Required tool(s) not found on your PATH:")
        for name in missing:
            print(f"   - {name}")
        print("   Install: docker, https://kind.sigs.k8s.io/, https://kubernetes.io/docs/tasks/tools/")
        return False
    return True


def main():
    if not require_binaries("docker", "kind", "kubectl"):
        return

    fastapi_tag = ask_tag("fastapi")
    vue_tag = ask_tag("vue")

    fastapi_image = f"speechtonote-backend:{fastapi_tag}"
    vue_image = f"speechtonote-frontend:{vue_tag}"

    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(script_dir, "../../backend/speech-to-note-backend")
    frontend_path = os.path.join(script_dir, "../../frontend")
    manifests_path = os.path.join(script_dir, "../../manifests")
    
    # Validate paths exist
    if not os.path.exists(backend_path):
        print(f"Erreur: Le répertoire backend n'existe pas: {os.path.abspath(backend_path)}")
        return
    if not os.path.exists(frontend_path):
        print(f"Erreur: Le répertoire frontend n'existe pas: {os.path.abspath(frontend_path)}")
        return
    if not os.path.exists(manifests_path):
        print(f"Erreur: Le répertoire manifests n'existe pas: {os.path.abspath(manifests_path)}")
        return

    print(f"Utilisation des images Docker : {fastapi_image} et {vue_image}")
    # Crée le cluster Kind s'il n'existe pas déjà
    clusters = subprocess.run(["kind", "get", "clusters"], capture_output=True, text=True)
    if "kub-speechtonote-app" not in clusters.stdout:
        print("Création du cluster Kind 'kub-speechtonote-app'...")
        kind_config_path = os.path.join(manifests_path, "kind-config.yaml")
        
        # Create host directory for persistent data (matches kind-config.yaml)
        host_data_dir = get_host_data_dir()
        os.makedirs(host_data_dir, exist_ok=True)
        
        subprocess.run([
            "kind", "create", "cluster", 
            "--name", "kub-speechtonote-app",
            "--config", kind_config_path
        ], check=True)
    else:
        print("Le cluster Kind 'kub-speechtonote-app' existe déjà.")

    # Build images
    if image_exists(fastapi_image):
        print(f"L'image {fastapi_image} existe déjà, construction ignorée.")
    else:
        print(f"Construction de l'image {fastapi_image}...")
        subprocess.run(["docker", "build", "-t", fastapi_image, os.path.abspath(backend_path)], check=True)
    
    if image_exists(vue_image):
        print(f"L'image {vue_image} existe déjà, construction ignorée.")
    else:
        print(f"Construction de l'image {vue_image}...")
        subprocess.run([
            "docker", "build", 
            "--build-arg", "VITE_CONFIG_ENV_FRONT=local_kub",
            "-t", vue_image, 
            os.path.abspath(frontend_path)
        ], check=True)

    # Charger les images dans Kind
    print(f"Chargement de l'image {fastapi_image} dans Kind...")
    subprocess.run(["kind", "load", "docker-image", fastapi_image, "--name", "kub-speechtonote-app"], check=True)
    print(f"Chargement de l'image {vue_image} dans Kind...")
    subprocess.run(["kind", "load", "docker-image", vue_image, "--name", "kub-speechtonote-app"], check=True)

    # Deploy in correct order (remove the old apply all at once)
    print("Déploiement séquentiel des services...")
    if not deploy_in_order(os.path.abspath(manifests_path)):
        print("Échec du déploiement!")
        return

    print("Déploiement terminé avec succès!")
    
    print("\n🎉 Application déployée avec succès!")
    print("\nPour accéder aux applications, utilisez:")
    print("python forwarding.py")
    print("\nOu utilisez les commandes manuelles:")
    print("python forwarding.py   # http://localhost:8080 (frontend), :8081 (API)")
    print("python kill_forwarding.py   # stop those port-forwards")

if __name__ == '__main__':
    main()