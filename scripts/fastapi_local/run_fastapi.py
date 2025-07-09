import subprocess
import os
import sys

# Obtenir le chemin vers le dossier backend/speech-to-note-backend
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, "..", "..", "backend", "speech-to-note-backend")
backend_dir = os.path.abspath(backend_dir)

print(f"📁 Répertoire backend: {backend_dir}")

# Vérifier que le fichier main.py existe
main_py_path = os.path.join(backend_dir, "main.py")
if not os.path.exists(main_py_path):
    print(f"❌ Erreur: main.py introuvable dans {backend_dir}")
    sys.exit(1)

cmd = [
    "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"
]

print("🚀 Lancement de l'API FastAPI en local")
print(f"📂 Répertoire de travail: {backend_dir}")
print("🌐 URL: http://127.0.0.1:8000")
print("📖 Documentation: http://127.0.0.1:8000/docs")

try:
    # Changer le répertoire de travail et lancer uvicorn
    subprocess.run(cmd, cwd=backend_dir, check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors du lancement de FastAPI: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n🛑 Arrêt de l'API FastAPI")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    sys.exit(1)