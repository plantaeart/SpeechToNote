import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
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
  private axiosInstance: AxiosInstance

  constructor(config: ApiConfig) {
    this.config = config
    this.axiosInstance = axios.create({
      baseURL: `${config.API_BASE_URL}${config.ENDPOINTS.SPEAKER_NOTES}`,
      timeout: config.API_TIMEOUT,
      headers: config.REQUEST_CONFIG.headers,
    })
  }

  /**
   * Create speaker notes
   */
  async createNotesFromAPI(request: SNCreateRequest): Promise<BaseResponse<SpeakerNote[]>> {
    try {
      const response: AxiosResponse<BaseResponse<SpeakerNote[]>> = await this.axiosInstance.post(
        '/',
        request,
      )

      if (!ResponseValidator.isBaseResponse<SpeakerNote[]>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<SpeakerNote[]>> = await this.axiosInstance.get('/')

      if (!ResponseValidator.isBaseResponse<SpeakerNote[]>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<SpeakerNote[]>> = await this.axiosInstance.put(
        '/',
        request,
      )

      if (!ResponseValidator.isBaseResponse<SpeakerNote[]>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<SingleDeleteResponse>> =
        await this.axiosInstance.delete(`/${id_note}`)

      if (!ResponseValidator.isBaseResponse<SingleDeleteResponse>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<DeleteResponse>> = await this.axiosInstance.delete(
        '/ids',
        { data: request },
      )

      if (!ResponseValidator.isBaseResponse<DeleteResponse>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<DeleteResponse>> =
        await this.axiosInstance.delete('/')

      if (!ResponseValidator.isBaseResponse<DeleteResponse>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to delete all speaker notes: ${error.message}`)
      }
      throw new Error('Failed to delete all speaker notes: Unknown error')
    }
  }
}
