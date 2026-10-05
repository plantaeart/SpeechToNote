import type { ApiConfig } from '@/models/ApiConfig'

// The API is reached through the port-forward started by
// scripts/kubernetes/forwarding.py. The NodePort (30002) is bound inside the
// kind node and is NOT reachable from the host.
export const ENV_KUB: ApiConfig = {
  API_BASE_URL: 'http://localhost:8081',
  API_TIMEOUT: 10000,
  ENVIRONMENT: 'local_kub',
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

export default ENV_KUB
