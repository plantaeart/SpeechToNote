import uvicorn
import sys

# Display configuration before starting
print("\n" + "🚀 " + "="*50, flush=True)
print("  SpeechToNote FastAPI Server Starting...", flush=True)
print("="*54, flush=True)

from app import app

if __name__ == "__main__":
    print("\n[MAIN] 🌐 Starting uvicorn server...", flush=True)
    print("[MAIN] 📍 URL: http://127.0.0.1:8000", flush=True)
    print("[MAIN] 📖 Docs: http://127.0.0.1:8000/docs", flush=True)
    print("="*54 + "\n", flush=True)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
