import ENV_LOCAL from './env.local'
import ENV_DOCKER from './env.local.docker'
import ENV_KUB from './env.local.kub'
import type { ApiConfig } from '@/models/ApiConfig'

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

type RuntimeEnv = {
  GCP_API_KEY?: string
  API_BASE_URL?: string
}

declare global {
  interface Window {
    __SPEECHTONOTE_ENV__?: RuntimeEnv
  }
}

/**
 * Reads the runtime values written by the Docker entrypoint (env.js).
 * Empty outside Docker, so the build-time constants below stay in charge.
 */
function getRuntimeEnv(): RuntimeEnv {
  if (typeof window === 'undefined') return {}
  return window.__SPEECHTONOTE_ENV__ ?? {}
}

/**
 * Gets the appropriate configuration based on the current environment.
 * @returns The configuration object for the current environment.
 */
export function getEnvironmentConfig() {
  let config: ApiConfig
  switch (CURRENT_ENV) {
    case 'local_docker':
      config = ENV_DOCKER
      break
    case 'local':
      config = ENV_LOCAL
      break
    case 'local_kub':
      config = ENV_KUB
      break
    default:
      console.warn(`Unknown environment: ${CURRENT_ENV}, falling back to local config`)
      config = ENV_LOCAL
  }

  const runtime = getRuntimeEnv()
  if (!runtime.GCP_API_KEY && !runtime.API_BASE_URL) return config

  return {
    ...config,
    GCP_API_KEY: runtime.GCP_API_KEY || config.GCP_API_KEY,
    API_BASE_URL: runtime.API_BASE_URL || config.API_BASE_URL,
  }
}
