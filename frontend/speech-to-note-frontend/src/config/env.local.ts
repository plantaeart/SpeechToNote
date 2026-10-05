import type { ApiConfig } from '@/models/ApiConfig'

// Fill in your own Google Cloud API key to enable speech recognition.
// See the "Generate a Google Cloud API key" section of the root README.
export const ENV_LOCAL: ApiConfig = {
  API_BASE_URL: 'http://127.0.0.1:8000',
  API_TIMEOUT: 10000,
  ENVIRONMENT: 'local',
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

export default ENV_LOCAL
