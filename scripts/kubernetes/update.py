import subprocess
import os

def ask_tag(service):
    tag = input(f"Entrez le tag Docker pour {service} (par défaut: latest) : ").strip()
    return tag if tag else "latest"

def build_and_load(service, path, tag):
    if service == "fastapi":
        image = f"speechtonote-backend:{tag}"
    else:
        image = f"speechtonote-frontend:{tag}"
    
    if not os.path.exists(path):
        print(f"Erreur: Le répertoire {service} n'existe pas: {os.path.abspath(path)}")
        return False
        
    print(f"Construction de l'image {image}...")
    subprocess.run(["docker", "build", "-t", image, os.path.abspath(path)], check=True)
    print(f"Chargement de l'image {image} dans Kind...")
    subprocess.run(["kind", "load", "docker-image", image, "--name", "kub-speechtonote-app"], check=True)
    return True

def rollout_restart(deployment):
    print(f"Redémarrage du déploiement {deployment}...")
    subprocess.run(["kubectl", "rollout", "restart", f"deployment/{deployment}"], check=True)

if __name__ == "__main__":
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(script_dir, "../../backend")
    frontend_path = os.path.join(script_dir, "../../frontend")
    
    fastapi_tag = ask_tag("fastapi")
    vue_tag = ask_tag("vue")

    if build_and_load("fastapi", backend_path, fastapi_tag):
        rollout_restart("fastapi")
    if build_and_load("vue", frontend_path, vue_tag):
        rollout_restart("vue")

    print("Mise à jour terminée !")
