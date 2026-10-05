import type { ApiConfig } from '@/models/ApiConfig'

// Same key as env.local.ts: speech recognition always calls Google directly
// from the browser, so the key is baked in at build time either way.
export const ENV_DOCKER: ApiConfig = {
  API_BASE_URL: 'http://localhost:8000',
  API_TIMEOUT: 10000,
  ENVIRONMENT: 'local_docker',
  DEBUG: true,
  GCP_API_KEY: '',
  ENDPOINTS: {
    SPEAKER_NOTES: '/speaker_notes',
    SPEAKER_COMMANDS: '/speaker_commands',
  },

  REQUEST_CONFIG: {
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    timeout: 10000,
  },
}

export default ENV_DOCKER
