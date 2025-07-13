import subprocess

def ask_tag(service):
    tag = input(f"Entrez le tag Docker pour {service} (par défaut: latest) : ").strip()
    return tag if tag else "latest"

def main():
    fastapi_tag = ask_tag("fastapi")
    vue_tag = ask_tag("vue")

    fastapi_image = f"my-fastapi:{fastapi_tag}"
    vue_image = f"my-vue:{vue_tag}"

    # Crée le cluster Kind s'il n'existe pas déjà
    clusters = subprocess.run(["kind", "get", "clusters"], capture_output=True, text=True)
    if "my-app" not in clusters.stdout:
        print("Création du cluster Kind 'my-app'...")
        subprocess.run(["kind", "create", "cluster", "--name", "my-app"], check=True)
    else:
        print("Le cluster Kind 'my-app' existe déjà.")

    # Build images
    print(f"Construction de l'image {fastapi_image}...")
    subprocess.run(["docker", "build", "-t", fastapi_image, "../backend"], check=True)
    print(f"Construction de l'image {vue_image}...")
    subprocess.run(["docker", "build", "-t", vue_image, "../frontend"], check=True)

    # Charger les images dans Kind
    print(f"Chargement de l'image {fastapi_image} dans Kind...")
    subprocess.run(["kind", "load", "docker-image", fastapi_image, "--name", "my-app"], check=True)
    print(f"Chargement de l'image {vue_image} dans Kind...")
    subprocess.run(["kind", "load", "docker-image", vue_image, "--name", "my-app"], check=True)

    # Appliquer les manifests Kubernetes
    print("Application des manifests Kubernetes...")
    subprocess.run(["kubectl", "apply", "-f", "../manifests/"], check=True)

    print("Déploiement terminé !")

if __name__ == '__main__':
    main()
