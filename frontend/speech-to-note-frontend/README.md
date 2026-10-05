# SpeechToNote — frontend

Vue 3 + TypeScript frontend. Records your voice, sends the audio to the Google
Cloud Speech-to-Text API and stores the resulting speaker notes through the
FastAPI backend.

## Setup

```bash
npm ci
```

## Configuration

The app reads its configuration from `src/config/`:

| File | Used for |
| --- | --- |
| `env.current.ts` | Selects the active config (build-time) |
| `env.local.ts` | Running against a local FastAPI on port 8000 |
| `env.local.docker.ts` | Running against the Docker backend |
| `env.local.kub.ts` | Running against the kind cluster |

Set `GCP_API_KEY` in the file for the environment you use. See the
[Generate a Google Cloud API key](../../README.md#generate-a-google-cloud-api-key)
section of the root README — the app ships with an empty key and does nothing
until you add yours.

To build for a specific environment:

```bash
VITE_CONFIG_ENV_FRONT=local_docker npm run build
```

## Run

```bash
npm run dev        # dev server on http://localhost:5173
npm run build      # type-check + production build
npm run preview    # serve the production build
```

The backend must be running for notes to be saved. Without a Google API key the
recording will fail — see the README above.

## Tests

```bash
npm run type-check   # vue-tsc
npm run lint         # eslint (read-only; use lint:fix to autofix)
npm run build        # production build
npm run test:unit    # vitest
npm run test:e2e     # builds, serves, then runs the Cypress specs
```

The end-to-end suite builds the app first, so it works on a fresh clone:

```bash
npm run test:e2e
# ✔ app.cy.ts — 1 passing
```

The suite is small so far: `tests/` covers the `Separator` component and
`cypress/e2e/` renders the app. `test:e2e:dev` opens the interactive Cypress
runner against the dev server.