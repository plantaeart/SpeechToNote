import subprocess
import sys

def kill_kubectl_processes():
    """Kill all kubectl port-forward processes"""
    try:
        # Find kubectl processes
        if sys.platform == "win32":
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq kubectl.exe', '/FO', 'CSV'],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if 'kubectl.exe' in line:
                    pid = line.split(',')[1].strip('"')
                    subprocess.run(['taskkill', '/PID', pid, '/F'])
                    print(f"✅ Processus kubectl PID {pid} terminé")
        else:
            subprocess.run(['pkill', '-f', 'kubectl.*port-forward'])
            print("✅ Tous les processus kubectl port-forward terminés")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    print("🛑 Arrêt des processus de port-forwarding...")
    kill_kubectl_processes()
    print("✅ Terminé!")
