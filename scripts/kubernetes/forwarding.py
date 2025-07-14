import subprocess
import threading
import time
import sys
import socket
import platform

def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def kill_process_using_port(port):
    """Kill process using the specified port"""
    try:
        if platform.system() == "Windows":
            # Find PID using the port
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                            print(f"✅ Processus PID {pid} utilisant le port {port} terminé")
                            return True
        else:
            # Unix/Linux/Mac
            result = subprocess.run(
                f'lsof -ti:{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(f'kill -9 {pid}', shell=True, capture_output=True)
                        print(f"✅ Processus PID {pid} utilisant le port {port} terminé")
                return True
    except Exception as e:
        print(f"❌ Erreur lors de l'arrêt du processus sur le port {port}: {e}")
    return False

def ensure_port_available(port):
    """Ensure port is available by killing process if needed"""
    if is_port_available(port):
        return True
    
    print(f"⚠️ Port {port} est utilisé, tentative d'arrêt du processus...")
    if kill_process_using_port(port):
        time.sleep(1)  # Wait a bit for process to fully terminate
        return is_port_available(port)
    return False

def port_forward_service(service_name, local_port, service_port):
    """Port forward a specific service"""
    print(f"Démarrage du port-forwarding pour {service_name}...")
    try:
        subprocess.run([
            "kubectl", "port-forward", 
            f"service/{service_name}", 
            f"{local_port}:{service_port}"
        ])
    except Exception as e:
        print(f"Erreur lors du port-forwarding de {service_name}: {e}")

def check_services_exist():
    """Check if the required services exist"""
    try:
        result = subprocess.run(
            ["kubectl", "get", "services", "-o", "name"], 
            capture_output=True, text=True, check=True
        )
        services = result.stdout.strip().split('\n')
        vue_exists = any('vue-service' in s for s in services)
        fastapi_exists = any('fastapi-service' in s for s in services)
        return vue_exists, fastapi_exists
    except subprocess.CalledProcessError:
        return False, False

def main():
    print("🔗 Script de Port-Forwarding pour SpeechToNote")
    print("=" * 50)
    
    # Check if services exist
    vue_exists, fastapi_exists = check_services_exist()
    
    if not vue_exists and not fastapi_exists:
        print("❌ Aucun service trouvé. Assurez-vous que l'application est déployée.")
        print("Exécutez d'abord start.py pour déployer l'application.")
        return
    
    print("Services détectés:")
    if vue_exists:
        print("✅ vue-service")
    if fastapi_exists:
        print("✅ fastapi-service")
    
    print("\nOptions de port-forwarding:")
    print("1. Port-forward tous les services")
    print("2. Port-forward uniquement Vue.js (frontend)")
    print("3. Port-forward uniquement FastAPI (backend)")
    print("4. Quitter")
    
    choice = input("\nChoisissez une option (1-4): ").strip()
    
    if choice == "1" and vue_exists and fastapi_exists:
        # Ensure ports are available, kill processes if needed
        vue_port = 8080
        fastapi_port = 30002
        
        if not ensure_port_available(vue_port):
            print(f"❌ Impossible de libérer le port {vue_port}")
            return
            
        if not ensure_port_available(fastapi_port):
            print(f"❌ Impossible de libérer le port {fastapi_port}")
            return
            
        print("\n🚀 Démarrage du port-forwarding pour tous les services...")
        print(f"Frontend (Vue): http://localhost:{vue_port}")
        print(f"Backend (FastAPI): http://localhost:{fastapi_port}/docs")
        print("\nAppuyez sur Ctrl+C pour arrêter")
        
        vue_thread = threading.Thread(target=port_forward_service, 
                                     args=("vue-service", str(vue_port), "80"), daemon=True)
        fastapi_thread = threading.Thread(target=port_forward_service, 
                                         args=("fastapi-service", str(fastapi_port), "8000"), daemon=True)
        
        vue_thread.start()
        fastapi_thread.start()
        
    elif choice == "2" and vue_exists:
        vue_port = 8080
        if not ensure_port_available(vue_port):
            print(f"❌ Impossible de libérer le port {vue_port}")
            return
            
        print("\n🚀 Démarrage du port-forwarding pour Vue.js...")
        print(f"Frontend (Vue): http://localhost:{vue_port}")
        print("\nAppuyez sur Ctrl+C pour arrêter")
        
        vue_thread = threading.Thread(target=port_forward_service, 
                                     args=("vue-service", str(vue_port), "80"), daemon=True)
        vue_thread.start()
        
    elif choice == "3" and fastapi_exists:
        fastapi_port = 8010
        if not ensure_port_available(fastapi_port):
            print(f"❌ Impossible de libérer le port {fastapi_port}")
            return
            
        print("\n🚀 Démarrage du port-forwarding pour FastAPI...")
        print(f"Backend (FastAPI): http://localhost:{fastapi_port}/docs")
        print("\nAppuyez sur Ctrl+C pour arrêter")
        
        fastapi_thread = threading.Thread(target=port_forward_service, 
                                         args=("fastapi-service", str(fastapi_port), "8000"), daemon=True)
        fastapi_thread.start()
        
    elif choice == "4":
        print("Au revoir!")
        return
    else:
        print("❌ Option invalide ou service non disponible.")
        return
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du port-forwarding...")
        print("Services arrêtés.")

if __name__ == '__main__':
    main()
