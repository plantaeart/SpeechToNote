"""CORS settings for the local API.

The app is intended for local development only, so the origins are the
localhost ports the Vite dev server and the Docker/Kubernetes deployments use.
Add your own origin here if you serve the frontend from somewhere else.
"""

CORS_CONFIG = {
    "allow_origins": [
        # Vite dev server, and the Docker Compose frontend (FRONTEND_PORT)
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Vite preview (npm run preview, used by the Cypress e2e run)
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        # kind cluster via scripts/kubernetes/forwarding.py
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        # the API the kind frontend calls (forwarding.py backend port)
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        # older local setups
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
