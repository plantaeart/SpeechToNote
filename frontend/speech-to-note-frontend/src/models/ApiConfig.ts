export interface ApiConfig {
  API_BASE_URL: string
  API_TIMEOUT: number
  ENVIRONMENT: string
  DEBUG: boolean
  ENDPOINTS: {
    SPEAKER_NOTES: string
    SPEAKER_COMMANDS: string
  }
  REQUEST_CONFIG: {
    headers: Record<string, string>
    timeout: number
  }
}
