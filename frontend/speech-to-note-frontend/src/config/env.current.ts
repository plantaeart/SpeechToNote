import ENV_LOCAL from './env.local'
import ENV_DOCKER from './env.local.docker'
import ENV_KUB from './env.local.kub'

export type EnvironmentType = 'local' | 'local_docker' | 'local_kub'

// Get environment from build-time environment variable or default to 'local'
const getEnvironmentFromEnv = (): EnvironmentType => {
  const envVar = import.meta.env.VITE_CONFIG_ENV_FRONT as EnvironmentType
  if (envVar && ['local', 'local_docker', 'local_kub'].includes(envVar)) {
    return envVar
  }
  return 'local' // Default fallback
}

console.log(`Current environment: ${getEnvironmentFromEnv()}`)
export const CURRENT_ENV: EnvironmentType = getEnvironmentFromEnv()
export const IS_DEBUG = false
export const VERSION = '1.0.1'
export const GCP_STT_API_COLLECT_EVERY_X_MS = 2000
export const GCP_STT_API_TRANSCRIBE_EVERY_X_MS = 3000
export const GCS_BUCKET_NAME = 'speech-to-note-bucket'

/**
 * Gets the appropriate configuration based on the current environment.
 * @returns The configuration object for the current environment.
 */
export function getEnvironmentConfig() {
  switch (CURRENT_ENV) {
    case 'local_docker':
      return ENV_DOCKER
    case 'local':
      return ENV_LOCAL
    case 'local_kub':
      return ENV_KUB
    default:
      console.warn(`Unknown environment: ${CURRENT_ENV}, falling back to local config`)
      return ENV_LOCAL
  }
}
