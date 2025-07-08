import subprocess

def delete_cluster():
    print("Suppression du cluster Kind 'my-app'...")
    subprocess.run(["kind", "delete", "cluster", "--name", "my-app"], check=True)
    print("Cluster supprimé.")

if __name__ == "__main__":
    delete_cluster()
