import type { ApiConfig } from '@/models/ApiConfig'
import { SpeakerCommand } from '../models/SpeakerCommand'
import type {
  SCCreateRequest,
  SCDeleteByIdsRequest,
  SCUpdateRequest,
} from '@/models/request/SCRequest'
import {
  ResponseValidator,
  type BaseResponse,
  type DeleteResponse,
  type SingleDeleteResponse,
} from '@/models/response/BaseResponse'

export class SpeakerCommandService {
  private config: ApiConfig
  private baseUrl: string

  constructor(config: ApiConfig) {
    this.config = config
    this.baseUrl = `${config.API_BASE_URL}${config.ENDPOINTS.SPEAKER_COMMANDS}`
  }

  /**
   * Create speaker commands
   */
  async createCommandsFromAPI(request: SCCreateRequest): Promise<BaseResponse<SpeakerCommand[]>> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: this.config.REQUEST_CONFIG.headers,
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<SpeakerCommand[]>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to create speaker commands: ${error.message}`)
      }
      throw new Error('Failed to create speaker commands: Unknown error')
    }
  }

  /**
   * Get all speaker commands
   */
  async getAllCommandsFromAPI(): Promise<BaseResponse<SpeakerCommand[]>> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'GET',
        headers: this.config.REQUEST_CONFIG.headers,
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<SpeakerCommand[]>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get speaker commands: ${error.message}`)
      }
      throw new Error('Failed to get speaker commands: Unknown error')
    }
  }

  /**
   * Update speaker commands
   */
  async updateCommandsFromAPI(request: SCUpdateRequest): Promise<BaseResponse<SpeakerCommand[]>> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'PUT',
        headers: this.config.REQUEST_CONFIG.headers,
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<SpeakerCommand[]>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to update speaker commands: ${error.message}`)
      }
      throw new Error('Failed to update speaker commands: Unknown error')
    }
  }

  /**
   * Delete speaker command by ID
   */
  async deleteCommandByIdFromAPI(id_command: number): Promise<BaseResponse<SingleDeleteResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/${id_command}`, {
        method: 'DELETE',
        headers: this.config.REQUEST_CONFIG.headers,
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<SingleDeleteResponse>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to delete speaker command: ${error.message}`)
      }
      throw new Error('Failed to delete speaker command: Unknown error')
    }
  }

  /**
   * Delete speaker commands by IDs
   */
  async deleteCommandsByIdsFromAPI(
    request: SCDeleteByIdsRequest,
  ): Promise<BaseResponse<DeleteResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/ids`, {
        method: 'DELETE',
        headers: this.config.REQUEST_CONFIG.headers,
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<DeleteResponse>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to delete speaker commands: ${error.message}`)
      }
      throw new Error('Failed to delete speaker commands: Unknown error')
    }
  }

  /**
   * Delete all speaker commands
   */
  async deleteAllCommandsFromAPI(): Promise<BaseResponse<DeleteResponse>> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'DELETE',
        headers: this.config.REQUEST_CONFIG.headers,
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<DeleteResponse>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to delete all speaker commands: ${error.message}`)
      }
      throw new Error('Failed to delete all speaker commands: Unknown error')
    }
  }
}
