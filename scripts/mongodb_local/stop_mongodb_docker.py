import subprocess

print("Arrêt et suppression du conteneur MongoDB local...")
subprocess.run(["docker", "rm", "-f", "mongo-local"], check=True)
print("Conteneur MongoDB local arrêté et supprimé.")
