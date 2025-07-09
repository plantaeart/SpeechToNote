import type { ApiConfig } from '@/models/ApiConfig'
import { SpeakerNote } from '../models/SpeakerNote'
import type {
  SNCreateRequest,
  SNDeleteByIdsRequest,
  SNUpdateRequest,
} from '@/models/request/SNRequest'
import {
  ResponseValidator,
  type BaseResponse,
  type DeleteResponse,
  type SingleDeleteResponse,
} from '@/models/response/BaseResponse'

export class SpeakerNoteService {
  private config: ApiConfig
  private baseUrl: string

  constructor(config: ApiConfig) {
    this.config = config
    this.baseUrl = `${config.API_BASE_URL}${config.ENDPOINTS.SPEAKER_NOTES}`
  }

  /**
   * Create speaker notes
   */
  async createNotesFromAPI(request: SNCreateRequest): Promise<BaseResponse<SpeakerNote[]>> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: this.config.REQUEST_CONFIG.headers,
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<SpeakerNote[]>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to create speaker notes: ${error.message}`)
      }
      throw new Error('Failed to create speaker notes: Unknown error')
    }
  }

  /**
   * Get all speaker notes
   */
  async getAllNotesFromAPI(): Promise<BaseResponse<SpeakerNote[]>> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'GET',
        headers: this.config.REQUEST_CONFIG.headers,
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<SpeakerNote[]>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get speaker notes: ${error.message}`)
      }
      throw new Error('Failed to get speaker notes: Unknown error')
    }
  }

  /**
   * Update speaker notes
   */
  async updateNotesFromAPI(request: SNUpdateRequest): Promise<BaseResponse<SpeakerNote[]>> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'PUT',
        headers: this.config.REQUEST_CONFIG.headers,
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(this.config.API_TIMEOUT),
      })

      const data = await response.json()

      if (!ResponseValidator.isBaseResponse<SpeakerNote[]>(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to update speaker notes: ${error.message}`)
      }
      throw new Error('Failed to update speaker notes: Unknown error')
    }
  }

  /**
   * Delete speaker note by ID
   */
  async deleteNoteByIdFromAPI(id_note: number): Promise<BaseResponse<SingleDeleteResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/${id_note}`, {
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
        throw new Error(`Failed to delete speaker note: ${error.message}`)
      }
      throw new Error('Failed to delete speaker note: Unknown error')
    }
  }

  /**
   * Delete speaker notes by IDs
   */
  async deleteNotesByIdsFromAPI(
    request: SNDeleteByIdsRequest,
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
        throw new Error(`Failed to delete speaker notes: ${error.message}`)
      }
      throw new Error('Failed to delete speaker notes: Unknown error')
    }
  }

  /**
   * Delete all speaker notes
   */
  async deleteAllNotesFromAPI(): Promise<BaseResponse<DeleteResponse>> {
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
        throw new Error(`Failed to delete all speaker notes: ${error.message}`)
      }
      throw new Error('Failed to delete all speaker notes: Unknown error')
    }
  }
}
