import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { SpeakerCommandService } from '../services/SpeakerCommandService'
import type { SpeakerCommand } from '@/models/SpeakerCommand'
import { ResponseValidator, type BaseResponse } from '@/models/response/BaseResponse'
import { SCRequestBuilder } from '@/models/request/SCRequest'
import { getEnvironmentConfig } from '@/config/env.current'

export const useSpeakerCommandStore = defineStore('speakerCommand', () => {
  // State
  const commands = ref<SpeakerCommand[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastResponse = ref<BaseResponse | null>(null)

  // Service instance
  const service = computed(() => new SpeakerCommandService(getEnvironmentConfig()))

  // Getters
  const commandsCount = computed(() => commands.value.length)
  const hasCommands = computed(() => commands.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)
  const sortedCommands = computed(() =>
    [...commands.value].sort((a, b) => a.id_command - b.id_command),
  )

  // Helper functions
  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  const handleResponse = <T>(response: BaseResponse<T>) => {
    lastResponse.value = response
    if (ResponseValidator.isErrorResponse(response)) {
      setError(response.message)
      return false
    }
    clearError()
    return true
  }

  // Actions
  const createCommandFromStore = async (
    command_name: string,
    command_vocal: string[],
    command_description?: string,
    html_tag_start?: string,
    html_tag_end?: string,
  ) => {
    setLoading(true)
    clearError()

    try {
      const request = SCRequestBuilder.createCommandRequestBuilder(
        command_name,
        command_vocal,
        command_description,
        html_tag_start,
        html_tag_end,
      )
      const response = await service.value.createCommandsFromAPI(request)

      if (handleResponse(response) && response.data) {
        commands.value.push(...response.data)
        return response.data
      }
      return null
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMsg)
      return null
    } finally {
      setLoading(false)
    }
  }

  const createCommandsFromStore = async (
    commandsToCreate: Array<{
      command_name: string
      command_vocal: string[]
      command_description?: string
      html_tag_start?: string
      html_tag_end?: string
    }>,
  ) => {
    setLoading(true)
    clearError()

    try {
      const request = SCRequestBuilder.createCommandsRequestBuilder(commandsToCreate)
      const response = await service.value.createCommandsFromAPI(request)

      if (handleResponse(response) && response.data) {
        commands.value.push(...response.data)
        return response.data
      }
      return null
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMsg)
      return null
    } finally {
      setLoading(false)
    }
  }

  const fetchAllCommandsFromStore = async () => {
    setLoading(true)
    clearError()

    try {
      const response = await service.value.getAllCommandsFromAPI()

      if (handleResponse(response) && response.data) {
        commands.value = response.data
        return response.data
      }
      return null
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMsg)
      return null
    } finally {
      setLoading(false)
    }
  }

  const updateCommandFromStore = async (
    id_command: number,
    updates: {
      command_name?: string
      command_vocal?: string[]
      command_description?: string
      html_tag_start?: string
      html_tag_end?: string
    },
  ) => {
    setLoading(true)
    clearError()

    try {
      const request = SCRequestBuilder.updateCommandRequestBuilder(id_command, updates)
      const response = await service.value.updateCommandsFromAPI(request)

      if (handleResponse(response) && response.data) {
        // Update local state
        const updatedCommand = response.data[0]
        const index = commands.value.findIndex((cmd) => cmd.id_command === id_command)
        if (index !== -1) {
          commands.value[index] = updatedCommand
        }
        return updatedCommand
      }
      return null
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMsg)
      return null
    } finally {
      setLoading(false)
    }
  }

  const deleteCommandFromStore = async (id_command: number) => {
    setLoading(true)
    clearError()

    try {
      const response = await service.value.deleteCommandByIdFromAPI(id_command)

      if (handleResponse(response)) {
        // Remove from local state
        commands.value = commands.value.filter((cmd) => cmd.id_command !== id_command)
        return true
      }
      return false
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMsg)
      return false
    } finally {
      setLoading(false)
    }
  }

  const deleteCommandsByIdsFromStore = async (ids_command: number[]) => {
    setLoading(true)
    clearError()

    try {
      const request = SCRequestBuilder.deleteByIdsRequestBuilder(ids_command)
      const response = await service.value.deleteCommandsByIdsFromAPI(request)

      if (handleResponse(response)) {
        // Remove from local state
        commands.value = commands.value.filter((cmd) => !ids_command.includes(cmd.id_command))
        return response.data
      }
      return null
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMsg)
      return null
    } finally {
      setLoading(false)
    }
  }

  const deleteAllCommandsFromStore = async () => {
    setLoading(true)
    clearError()

    try {
      const response = await service.value.deleteAllCommandsFromAPI()

      if (handleResponse(response)) {
        commands.value = []
        return response.data
      }
      return null
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMsg)
      return null
    } finally {
      setLoading(false)
    }
  }

  const findCommandByIdFromStore = (id_command: number) => {
    return commands.value.find((cmd) => cmd.id_command === id_command)
  }

  const findCommandByNameFromStore = (command_name: string) => {
    return commands.value.find((cmd) => cmd.command_name === command_name)
  }

  const findCommandByVocalFromStore = (command_vocal: string) => {
    return commands.value.find((cmd) =>
      cmd.command_vocal.some((vocal) => vocal.toLowerCase() === command_vocal.toLowerCase()),
    )
  }

  const filterCommandsByNameFromStore = (searchTerm: string) => {
    return commands.value.filter((cmd) =>
      cmd.command_name.toLowerCase().includes(searchTerm.toLowerCase()),
    )
  }

  const filterCommandsByVocalFromStore = (searchTerm: string) => {
    return commands.value.filter((cmd) =>
      cmd.command_vocal.some((vocal) => vocal.toLowerCase().includes(searchTerm.toLowerCase())),
    )
  }

  const filterCommandsByDescriptionFromStore = (searchTerm: string) => {
    return commands.value.filter((cmd) =>
      cmd.command_description?.toLowerCase().includes(searchTerm.toLowerCase()),
    )
  }

  return {
    // State
    commands,
    loading,
    error,
    lastResponse,

    // Getters
    commandsCount,
    hasCommands,
    isLoading,
    hasError,
    sortedCommands,

    // Actions
    createCommandFromStore,
    createCommandsFromStore,
    fetchAllCommandsFromStore,
    updateCommandFromStore,
    deleteCommandFromStore,
    deleteCommandsByIdsFromStore,
    deleteAllCommandsFromStore,
    findCommandByIdFromStore,
    findCommandByNameFromStore,
    findCommandByVocalFromStore,
    filterCommandsByNameFromStore,
    filterCommandsByVocalFromStore,
    filterCommandsByDescriptionFromStore,
    clearError,
  }
})
