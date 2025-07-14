import subprocess

def delete_cluster():
    print("Suppression du cluster Kind 'kub-speechtonote-app'...")
    subprocess.run(["kind", "delete", "cluster", "--name", "kub-speechtonote-app"], check=True)
    print("Cluster supprimé.")

if __name__ == "__main__":
    delete_cluster()
