import subprocess
import os

volume_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./mongodb-data-local"))
os.makedirs(volume_path, exist_ok=True)

cmd = [
    "docker", "run", "-d",
    "--name", "mongo-local",
    "-p", "27017:27017",
    "-v", f"{volume_path}:/data/db",
    "mongo:6.0"
]

print("Lancement du conteneur MongoDB local avec persistance...")
print(cmd)
subprocess.run(cmd, check=True)
print("MongoDB local lancé sur le port 27017 avec persistance dans 'mongodb-data/'")
