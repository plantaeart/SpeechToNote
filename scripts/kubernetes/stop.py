import shutil
import subprocess

CLUSTER_NAME = "kub-speechtonote-app"


def delete_cluster():
    if shutil.which("kind") is None:
        print("❌ kind was not found on your PATH.")
        print("   Install it from https://kind.sigs.k8s.io/")
        return

    print(f"Suppression du cluster Kind '{CLUSTER_NAME}'...")
    result = subprocess.run(
        ["kind", "delete", "cluster", "--name", CLUSTER_NAME],
        capture_output=True,
        text=True,
    )
    print(result.stdout.strip() or result.stderr.strip())
    if result.returncode != 0:
        print("❌ Failed to delete the cluster.")
        return
    print("Cluster supprimé.")


if __name__ == "__main__":
    delete_cluster()