import type { ApiConfig } from '@/models/ApiConfig'

export const ENV_LOCAL: ApiConfig = {
  API_BASE_URL: 'http://127.0.0.1:8000',
  API_TIMEOUT: 10000,
  ENVIRONMENT: 'local',
  DEBUG: true,
  GCP_API_KEY: 'AIzaSyDPvvfLv6p68RIpGikJ8PhkcRnEli3ixkQ',
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
