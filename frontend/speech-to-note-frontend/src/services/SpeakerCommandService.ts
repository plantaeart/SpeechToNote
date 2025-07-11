import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
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
  private axiosInstance: AxiosInstance

  constructor(config: ApiConfig) {
    this.config = config
    this.axiosInstance = axios.create({
      baseURL: `${config.API_BASE_URL}${config.ENDPOINTS.SPEAKER_COMMANDS}`,
      timeout: config.API_TIMEOUT,
      headers: config.REQUEST_CONFIG.headers,
    })
  }

  /**
   * Create speaker commands
   */
  async createCommandsFromAPI(request: SCCreateRequest): Promise<BaseResponse<SpeakerCommand[]>> {
    try {
      const response: AxiosResponse<BaseResponse<SpeakerCommand[]>> = await this.axiosInstance.post(
        '/',
        request,
      )

      if (!ResponseValidator.isBaseResponse<SpeakerCommand[]>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<SpeakerCommand[]>> =
        await this.axiosInstance.get('/')

      if (!ResponseValidator.isBaseResponse<SpeakerCommand[]>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<SpeakerCommand[]>> = await this.axiosInstance.put(
        '/',
        request,
      )

      if (!ResponseValidator.isBaseResponse<SpeakerCommand[]>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<SingleDeleteResponse>> =
        await this.axiosInstance.delete(`/${id_command}`)

      if (!ResponseValidator.isBaseResponse<SingleDeleteResponse>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
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
      const response: AxiosResponse<BaseResponse<DeleteResponse>> =
        await this.axiosInstance.delete('/')

      if (!ResponseValidator.isBaseResponse<DeleteResponse>(response.data)) {
        throw new Error('Invalid response format')
      }

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to delete all speaker commands: ${error.message}`)
      }
      throw new Error('Failed to delete all speaker commands: Unknown error')
    }
  }
}
