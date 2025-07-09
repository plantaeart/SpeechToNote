/**
 * Speaker Note Create Model
 */
export interface SpeakerNoteCreate {
  title: string
  content: string
  commands?: string[]
}

/**
 * Speaker Note Update Model
 */
export interface SpeakerNoteUpdate {
  id_note: number
  title?: string
  content?: string
  commands?: string[]
}

/**
 * Speaker Notes Create Request
 */
export interface SNCreateRequest {
  data: SpeakerNoteCreate[]
}

/**
 * Speaker Notes Update Request
 */
export interface SNUpdateRequest {
  data: SpeakerNoteUpdate[]
}

/**
 * Speaker Notes Delete By IDs Request
 */
export interface SNDeleteByIdsRequest {
  ids_note: number[]
}

/**
 * Helper class for creating Speaker Note requests
 */
export class SNRequestBuilder {
  static createNoteRequestBuilder(
    title: string,
    content: string,
    commands: string[] = [],
  ): SNCreateRequest {
    if (!title.trim()) {
      throw new Error('Title is required')
    }
    if (!content.trim()) {
      throw new Error('Content is required')
    }
    if (title.length > 200) {
      throw new Error('Title must be 200 characters or less')
    }

    return {
      data: [
        {
          title: title.trim(),
          content: content.trim(),
          commands,
        },
      ],
    }
  }

  static createNotesRequestBuilder(notes: SpeakerNoteCreate[]): SNCreateRequest {
    notes.forEach((note) => {
      if (!note.title?.trim()) {
        throw new Error('All notes must have a title')
      }
      if (!note.content?.trim()) {
        throw new Error('All notes must have content')
      }
      if (note.title.length > 200) {
        throw new Error('All titles must be 200 characters or less')
      }
    })

    return { data: notes }
  }

  static updateNoteRequestBuilder(
    id_note: number,
    updates: Partial<Omit<SpeakerNoteUpdate, 'id_note'>>,
  ): SNUpdateRequest {
    if (!id_note || id_note <= 0) {
      throw new Error('Valid id_note is required for update')
    }
    if (updates.title !== undefined && updates.title.length > 200) {
      throw new Error('Title must be 200 characters or less')
    }

    return {
      data: [
        {
          id_note,
          ...updates,
        },
      ],
    }
  }

  static updateNotesRequestBuilder(updates: SpeakerNoteUpdate[]): SNUpdateRequest {
    updates.forEach((update) => {
      if (!update.id_note || update.id_note <= 0) {
        throw new Error('All updates must have a valid id_note')
      }
      if (update.title !== undefined && update.title.length > 200) {
        throw new Error('All titles must be 200 characters or less')
      }
    })

    return { data: updates }
  }

  static deleteByIdsRequestBuilder(ids_note: number[]): SNDeleteByIdsRequest {
    if (!ids_note.length) {
      throw new Error('At least one ID is required')
    }
    ids_note.forEach((id) => {
      if (!id || id <= 0) {
        throw new Error('All IDs must be valid positive numbers')
      }
    })

    return { ids_note }
  }
}
