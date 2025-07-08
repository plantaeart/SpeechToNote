import subprocess

def get_image_versions():
    result = subprocess.run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"], capture_output=True, text=True)
    images = result.stdout.strip().split('\n')

    fastapi_versions = [img for img in images if img.startswith("my-fastapi:")]
    vue_versions = [img for img in images if img.startswith("my-vue:")]

    print("Versions des images FastAPI disponibles :")
    for v in fastapi_versions:
        print(f" - {v}")

    print("\nVersions des images Vue.js disponibles :")
    for v in vue_versions:
        print(f" - {v}")

if __name__ == '__main__':
    get_image_versions()
