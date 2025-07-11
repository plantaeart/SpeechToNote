/**
 * Speaker Command Create Model
 */
export interface SpeakerCommandCreate {
  command_name: string
  command_vocal: string[]
  command_description?: string
  html_tag_start?: string
  html_tag_end?: string
}

/**
 * Speaker Command Update Model
 */
export interface SpeakerCommandUpdate {
  id_command: number
  command_name?: string
  command_vocal?: string[]
  command_description?: string
  html_tag_start?: string
  html_tag_end?: string
}

/**
 * Speaker Commands Create Request
 */
export interface SCCreateRequest {
  data: SpeakerCommandCreate[]
}

/**
 * Speaker Commands Update Request
 */
export interface SCUpdateRequest {
  data: SpeakerCommandUpdate[]
}

/**
 * Speaker Commands Delete By IDs Request
 */
export interface SCDeleteByIdsRequest {
  ids_command: number[]
}

/**
 * Helper class for creating Speaker Command requests
 */
export class SCRequestBuilder {
  static createCommandRequestBuilder(
    command_name: string,
    command_vocal: string[],
    command_description?: string,
    html_tag_start?: string,
    html_tag_end?: string,
  ): SCCreateRequest {
    if (!command_name.trim()) {
      throw new Error('Command name is required')
    }
    if (!command_vocal.length || !command_vocal.every((vocal) => vocal.trim())) {
      throw new Error('At least one non-empty command vocal is required')
    }
    if (command_name.length > 100) {
      throw new Error('Command name must be 100 characters or less')
    }
    if (html_tag_start && html_tag_start.length > 50) {
      throw new Error('HTML tag start must be 50 characters or less')
    }
    if (html_tag_end && html_tag_end.length > 50) {
      throw new Error('HTML tag end must be 50 characters or less')
    }

    return {
      data: [
        {
          command_name: command_name.trim(),
          command_vocal: command_vocal.map((vocal) => vocal.trim()),
          command_description: command_description?.trim(),
          html_tag_start: html_tag_start?.trim(),
          html_tag_end: html_tag_end?.trim(),
        },
      ],
    }
  }

  static createCommandsRequestBuilder(commands: SpeakerCommandCreate[]): SCCreateRequest {
    commands.forEach((command) => {
      if (!command.command_name?.trim()) {
        throw new Error('All commands must have a command_name')
      }
      if (!command.command_vocal?.length || !command.command_vocal.every((vocal) => vocal.trim())) {
        throw new Error('All commands must have at least one non-empty command_vocal')
      }
      if (command.command_name.length > 100) {
        throw new Error('All command names must be 100 characters or less')
      }
      if (command.html_tag_start && command.html_tag_start.length > 50) {
        throw new Error('All HTML tag starts must be 50 characters or less')
      }
      if (command.html_tag_end && command.html_tag_end.length > 50) {
        throw new Error('All HTML tag ends must be 50 characters or less')
      }
    })

    return { data: commands }
  }

  static updateCommandRequestBuilder(
    id_command: number,
    updates: Partial<Omit<SpeakerCommandUpdate, 'id_command'>>,
  ): SCUpdateRequest {
    if (!id_command || id_command <= 0) {
      throw new Error('Valid id_command is required for update')
    }
    if (updates.command_name !== undefined && updates.command_name.length > 100) {
      throw new Error('Command name must be 100 characters or less')
    }
    if (
      updates.command_vocal !== undefined &&
      (!updates.command_vocal.length || !updates.command_vocal.every((vocal) => vocal.trim()))
    ) {
      throw new Error('Command vocal must contain at least one non-empty string')
    }
    if (updates.html_tag_start !== undefined && updates.html_tag_start.length > 50) {
      throw new Error('HTML tag start must be 50 characters or less')
    }
    if (updates.html_tag_end !== undefined && updates.html_tag_end.length > 50) {
      throw new Error('HTML tag end must be 50 characters or less')
    }

    return {
      data: [
        {
          id_command,
          ...updates,
        },
      ],
    }
  }

  static updateCommandsRequestBuilder(updates: SpeakerCommandUpdate[]): SCUpdateRequest {
    updates.forEach((update) => {
      if (!update.id_command || update.id_command <= 0) {
        throw new Error('All updates must have a valid id_command')
      }
      if (update.command_name !== undefined && update.command_name.length > 100) {
        throw new Error('All command names must be 100 characters or less')
      }
      if (
        update.command_vocal !== undefined &&
        (!update.command_vocal.length || !update.command_vocal.every((vocal) => vocal.trim()))
      ) {
        throw new Error('All command vocals must contain at least one non-empty string')
      }
      if (update.html_tag_start !== undefined && update.html_tag_start.length > 50) {
        throw new Error('All HTML tag starts must be 50 characters or less')
      }
      if (update.html_tag_end !== undefined && update.html_tag_end.length > 50) {
        throw new Error('All HTML tag ends must be 50 characters or less')
      }
    })

    return { data: updates }
  }

  static deleteByIdsRequestBuilder(ids_command: number[]): SCDeleteByIdsRequest {
    if (!ids_command.length) {
      throw new Error('At least one ID is required')
    }
    ids_command.forEach((id) => {
      if (!id || id <= 0) {
        throw new Error('All IDs must be valid positive numbers')
      }
    })

    return { ids_command }
  }
}
