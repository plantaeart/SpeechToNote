# SpeechToNote

A voice-driven note-taking app: speak into your browser, the transcript becomes
structured speaker notes with commands, stored in MongoDB and analysed with
DuckDB.

Built as a full-stack experiment with Vue 3, FastAPI, MongoDB and DuckDB.

> **Run it with Docker:** add your Google API key to `infra/.env` (see
> [Generate a Google Cloud API key](#generate-a-google-cloud-api-key)), then
> `uv run --project scripts python scripts/infra_local/up.py` — that starts
> MongoDB, the API and the frontend together.

> **Note:** this project is built for **local development**. It has no
> authentication, so do not expose it to an untrusted network.

## Stack

| Layer      | Technology                                                     |
| ---------- | -------------------------------------------------------------- |
| Frontend   | Vue 3, TypeScript, Vite, Pinia, PrimeVue                       |
| Backend    | Python 3.13, FastAPI, Pydantic                                 |
| Database   | MongoDB                                                        |
| Analytics  | DuckDB                                                         |
| Speech     | Google Cloud Speech-to-Text (`v1/speech:recognize`)            |
| Tooling    | uv, Docker, kind (Kubernetes in Docker)                        |

## Requirements

For the Docker setup (recommended):

- [Docker](https://docs.docker.com/get-docker/) with Compose v2
- [uv](https://docs.astral.sh/uv/) — only to run the `up`/`down` helper scripts
  (or drive `docker compose` directly and skip this)
- A Google Cloud project and an **API key** for speech recognition. Set it in
  `infra/.env` before starting — steps in
  [Generate a Google Cloud API key](#generate-a-google-cloud-api-key).
  Optional: the app starts without it, but recording will not work.

For local development you also need:

- [Node.js](https://nodejs.org/) 20.19+ or 22.12+ (required by Vite 7)
- [Python](https://www.python.org/) 3.13 (pinned via `.python-version`)

## Quick start (Docker)

The recommended way to run SpeechToNote is with Docker Compose — it starts
MongoDB, the API and the frontend together, with no Python or Node setup.

```bash
git clone https://github.com/plantaeart/SpeechToNote.git
cd SpeechToNote
```

**Step 1 — add your Google Cloud API key** (needed for speech recognition).
It takes about five minutes: create a project, enable the Speech-to-Text API,
enable billing, then create an API key. Full steps are in
[Generate a Google Cloud API key](#generate-a-google-cloud-api-key).

```bash
cp infra/.env.example infra/.env
# then edit infra/.env and set:  GCP_API_KEY=your-key-here
```

You can skip this and start without a key — the app runs, but recording does
nothing. Setting it before you start means you don't have to restart anything:
the key is injected when the container starts, and is never baked into the image.

**Step 2 — start the stack:**

```bash
uv run --project scripts python scripts/infra_local/up.py
```

That builds the images, starts the stack and waits until the API answers:

```
✅ SpeechToNote is up
   Frontend  http://localhost:5173
   API docs  http://localhost:8000/docs
```

Stop it with:

```bash
uv run --project scripts python scripts/infra_local/down.py
```

- Frontend — <http://localhost:5173>
- API docs — <http://localhost:8000/docs>

Notes:

- Your Google API key is injected **when the container starts**, not baked into
  the image, so it never lands in an image layer. Change it in `infra/.env` and
  run `up` again.
- MongoDB is not published on the host — it exists only inside the compose
  network, so it cannot collide with a MongoDB you already run on 27017.
- Data lives in a named volume. `down.py --volumes` deletes it.
- Prefer plain compose? Use:
  ```bash
  docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build
  docker compose -f infra/docker-compose.yml --env-file infra/.env down
  ```

The app runs without a Google API key; speech recognition is simply disabled
until you add one.

## Run it locally instead

If you want hot reload while developing, run the three pieces separately. Start
MongoDB, then the backend and the frontend:

```bash
git clone https://github.com/plantaeart/SpeechToNote.git
cd SpeechToNote

# 1. MongoDB
docker run -d --name speechtonote-mongo -p 27017:27017 mongo:7

# 2. Backend  (http://127.0.0.1:8000)
cd backend/speech-to-note-backend
uv sync
uv run fastapi dev --port 8000

# 3. Frontend, in a second terminal  (http://localhost:5173)
cd frontend/speech-to-note-frontend
npm ci
npm run dev
```

Requires Node.js 20.19+ or 22.12+ and Python 3.13 with
[uv](https://docs.astral.sh/uv/).

### Backend configuration

Configuration is per-environment, selected with `CURRENT_ENV`
(`local`, `docker`, `kubernetes`). Defaults work out of the box; override them
with a `.env` file:

```bash
cd backend/speech-to-note-backend
cp .env.example .env
```

`.env` is gitignored. Without it, the app uses `mongodb://localhost:27017` and
database `speechtonote`.

## Generate a Google Cloud API key

Speech recognition uses the Google Cloud **Speech-to-Text v1 REST API**, called
directly from the browser. You need your own key:

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Cloud Speech-to-Text API** for that project.
3. Enable **billing** — Speech-to-Text is a paid API. Without billing the key
   returns `PERMISSION_DENIED`.
4. Go to **APIs & Services → Credentials** and click **Create credentials → API key**.
5. Copy the key and add it to your setup:

   **Docker (recommended)** — put it in `infra/.env`:

   ```bash
   cp infra/.env.example infra/.env
   # edit infra/.env and set GCP_API_KEY=your-key-here
   uv run --project scripts python scripts/infra_local/up.py
   ```

   The key is injected into the frontend **when the container starts**, so it
   never ends up in an image layer. Changing it means running `up` again.

   **Local development** — paste it into the config file for your environment:

   ```
   frontend/speech-to-note-frontend/src/config/env.local.ts
   ```

   ```ts
   GCP_API_KEY: 'your-key-here',
   ```

   Use `env.local.docker.ts` when running against a local Docker backend, and
   `env.local.kub.ts` for the kind cluster.

6. For local use, restrict the key under **API restrictions** (limit it to the
   Speech-to-Text API) and, if you deploy, add **HTTP referrer restrictions**.

Speech-to-Text usage is billed to your project. The app ships with an empty key,
so a clone never calls the API until you add your own.

## Project layout

```
infra/                      Docker Compose stack (the recommended way to run)
  docker-compose.yml        mongo + backend + frontend on one network
  .env.example              your GCP key and host ports
backend/
  speech-to-note-backend/   FastAPI app (routes, models, migrations)
  duck-db/                  DuckDB analytics over the MongoDB data
frontend/
  speech-to-note-frontend/  Vue 3 app
  Dockerfile                frontend image (nginx)
  docker-entrypoint.sh      writes env.js from env vars at container start
manifests/                  kind / Kubernetes manifests for local use
scripts/                    helpers for Docker Compose, MongoDB and kind
  infra_local/up.py         build + start the stack, wait until it answers
  infra_local/down.py       stop the stack
```

Each Python folder is its own `uv` project with its own lockfile.

## Tests

```bash
# Backend — the route tests need a MongoDB; they skip cleanly without one
cd backend/speech-to-note-backend
uv run pytest

# Backend config tests only (no database required)
uv run pytest tests/test_config.py

# Scripts helpers
cd scripts
uv sync
uv run pytest

# Frontend build, lint, type-check and tests
cd frontend/speech-to-note-frontend
npm run build
npm run lint         # eslint, read-only
npm run lint:fix     # applies the automatic fixes
npm run type-check
npm run test:unit
npm run test:e2e     # builds, serves, then runs Cypress
```

The backend suite runs against a **real** MongoDB: it uses the
`<database>_test` database and drops it when finished. Tests skip themselves if
no MongoDB is reachable at `MONGO_URI`.

## Local Kubernetes (optional)

Requires [kind](https://kind.sigs.k8s.io/) and [kubectl](https://kubernetes.io/docs/tasks/tools/).

```bash
cd scripts
uv run python kubernetes/start.py      # create the kind cluster and deploy
uv run python kubernetes/forwarding.py # optional: port-forward 8080 / 8081
uv run python kubernetes/kill_forwarding.py  # stop only those forwards
uv run python kubernetes/stop.py       # delete the cluster
```

Manifests live in `manifests/`. Images are built locally and loaded into kind
(`imagePullPolicy: Never`), so no registry is needed.

The services are exposed as NodePorts, which are reachable **from inside the
kind node**:

| Service  | NodePort | Service name       |
| -------- | -------- | ------------------ |
| API      | 30002    | `fastapi-service`  |
| Frontend | 30080    | `vue-service`      |

NodePorts are published on the cluster node, not on your host, so use
`forwarding.py` to reach them from the browser:

| Service  | Local port | URL                       |
| -------- | ---------- | ------------------------- |
| Frontend | 8080       | <http://localhost:8080>   |
| API      | 8081       | <http://localhost:8081>   |

`forwarding.py` uses 8080 and 8081 so they never collide with the NodePorts,
and it **never kills a process** — if a port is busy it prints the owning PID
and stops.

Port-forwards started by `forwarding.py` are recorded in
`infra/.local/port-forwards.json` (gitignored). `kill_forwarding.py` stops only
those PIDs, and re-checks each one is still a `kubectl port-forward` first, so
unrelated kubectl processes on your machine are left alone.

### MongoDB data on Windows

`manifests/kind-config.yaml` bind-mounts a host directory into the kind node.
The committed default is the POSIX path `/tmp/speechtonote-mongo-data`; on
Windows, edit `hostPath` to an absolute path such as `C:/temp/speechtonote-mongo-data`.
`start.py` creates the directory it uses, so keep the two in sync — or set
`SPEECHTONOTE_DATA_DIR` for the script and update the manifest to match.

## License

MIT — see [LICENSE](LICENSE).
