import type { ApiConfig } from '@/models/ApiConfig'

export const ENV_DOCKER: ApiConfig = {
  API_BASE_URL: 'http://localhost:8000',
  API_TIMEOUT: 15000,
  ENVIRONMENT: 'docker',
  DEBUG: false,

  ENDPOINTS: {
    SPEAKER_NOTES: '/speaker_notes',
    SPEAKER_COMMANDS: '/speaker_commands',
  },

  REQUEST_CONFIG: {
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    timeout: 15000,
  },
}

export default ENV_DOCKER
