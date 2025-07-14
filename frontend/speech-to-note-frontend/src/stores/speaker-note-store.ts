import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { SpeakerNoteService } from '../services/SpeakerNoteService'
import type { SpeakerNote } from '@/models/SpeakerNote'
import { ResponseValidator, type BaseResponse } from '@/models/response/BaseResponse'
import { SNRequestBuilder } from '@/models/request/SNRequest'
import { getEnvironmentConfig } from '@/config/env.current'

export const useSpeakerNoteStore = defineStore('speakerNote', () => {
  // State
  const notes = ref<SpeakerNote[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastResponse = ref<BaseResponse | null>(null)

  // Service instance
  const service = computed(() => new SpeakerNoteService(getEnvironmentConfig()))

  // Getters
  const notesCount = computed(() => notes.value.length)
  const hasNotes = computed(() => notes.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)
  const sortedNotes = computed(() => [...notes.value].sort((a, b) => b.id_note - a.id_note))

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
  const createNoteFromStore = async (title: string, content: string, commands: string[] = []) => {
    setLoading(true)
    clearError()

    try {
      const request = SNRequestBuilder.createNoteRequestBuilder(title, content, commands)
      const response = await service.value.createNotesFromAPI(request)

      if (handleResponse(response) && response.data) {
        notes.value.push(...response.data)
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

  const createNotesFromStore = async (
    notesToCreate: Array<{
      title: string
      content: string
      commands?: string[]
    }>,
  ) => {
    setLoading(true)
    clearError()

    try {
      const request = SNRequestBuilder.createNotesRequestBuilder(
        notesToCreate.map((note) => ({
          title: note.title,
          content: note.content,
          commands: note.commands || [],
        })),
      )

      const response = await service.value.createNotesFromAPI(request)

      if (handleResponse(response) && response.data) {
        notes.value.push(...response.data)
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

  const fetchAllNotesFromStore = async () => {
    setLoading(true)
    clearError()

    try {
      const response = await service.value.getAllNotesFromAPI()

      if (handleResponse(response) && response.data) {
        notes.value = response.data
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

  const updateNoteFromStore = async (
    id_note: number,
    updates: { title?: string; content?: string; commands?: string[] },
  ) => {
    setLoading(true)
    clearError()

    try {
      const request = SNRequestBuilder.updateNoteRequestBuilder(id_note, updates)
      const response = await service.value.updateNotesFromAPI(request)

      if (handleResponse(response) && response.data) {
        // Update local state
        const updatedNote = response.data[0]
        const index = notes.value.findIndex((note) => note.id_note === id_note)
        if (index !== -1) {
          notes.value[index] = updatedNote
        }
        return updatedNote
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

  const deleteNoteFromStore = async (id_note: number) => {
    setLoading(true)
    clearError()

    try {
      const response = await service.value.deleteNoteByIdFromAPI(id_note)

      if (handleResponse(response)) {
        // Remove from local state
        notes.value = notes.value.filter((note) => note.id_note !== id_note)
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

  const deleteNotesByIdsFromStore = async (ids_note: number[]) => {
    setLoading(true)
    clearError()

    try {
      const request = SNRequestBuilder.deleteByIdsRequestBuilder(ids_note)
      const response = await service.value.deleteNotesByIdsFromAPI(request)

      if (handleResponse(response)) {
        // Remove from local state
        notes.value = notes.value.filter((note) => !ids_note.includes(note.id_note))
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

  const deleteAllNotesFromStore = async () => {
    setLoading(true)
    clearError()

    try {
      const response = await service.value.deleteAllNotesFromAPI()

      if (handleResponse(response)) {
        notes.value = []
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

  const findNoteByIdFromStore = (id_note: number) => {
    return notes.value.find((note) => note.id_note === id_note)
  }

  const filterNotesByTitleFromStore = (searchTerm: string) => {
    return notes.value.filter((note) => note.title.toLowerCase().includes(searchTerm.toLowerCase()))
  }

  const filterNotesByContentFromStore = (searchTerm: string) => {
    return notes.value.filter((note) =>
      note.content.toLowerCase().includes(searchTerm.toLowerCase()),
    )
  }

  const filterNotesByCommandFromStore = (command: string) => {
    return notes.value.filter((note) => note.commands.includes(command))
  }

  return {
    // State
    notes,
    loading,
    error,
    lastResponse,

    // Getters
    notesCount,
    hasNotes,
    isLoading,
    hasError,
    sortedNotes,

    // Actions
    createNoteFromStore,
    createNotesFromStore,
    fetchAllNotesFromStore,
    updateNoteFromStore,
    deleteNoteFromStore,
    deleteNotesByIdsFromStore,
    deleteAllNotesFromStore,
    findNoteByIdFromStore,
    filterNotesByTitleFromStore,
    filterNotesByContentFromStore,
    filterNotesByCommandFromStore,
    clearError,
  }
})
