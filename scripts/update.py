import subprocess

def ask_tag(service):
    tag = input(f"Entrez le tag Docker pour {service} (par défaut: latest) : ").strip()
    return tag if tag else "latest"

def build_and_load(service, path, tag):
    image = f"my-{service}:{tag}"
    print(f"Construction de l'image {image}...")
    subprocess.run(["docker", "build", "-t", image, path], check=True)
    print(f"Chargement de l'image {image} dans Kind...")
    subprocess.run(["kind", "load", "docker-image", image, "--name", "my-app"], check=True)

def rollout_restart(deployment):
    print(f"Redémarrage du déploiement {deployment}...")
    subprocess.run(["kubectl", "rollout", "restart", f"deployment/{deployment}"], check=True)

if __name__ == "__main__":
    fastapi_tag = ask_tag("fastapi")
    vue_tag = ask_tag("vue")

    build_and_load("fastapi", "../backend", fastapi_tag)
    build_and_load("vue", "../frontend", vue_tag)

    rollout_restart("fastapi")
    rollout_restart("vue")

    print("Mise à jour terminée !")
