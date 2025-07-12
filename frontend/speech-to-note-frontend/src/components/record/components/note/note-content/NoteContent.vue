<script setup lang="ts">
import Editor from 'primevue/editor'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import InputText from 'primevue/inputtext'
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { GoogleSpeechService } from '@/services/GoogleSpeechService'
import { useSpeakerNoteStore } from '@/stores/speaker-note-store'
import { useRecordingStore } from '@/stores/recording-store'
import { useSpeakerCommandStore } from '@/stores/speaker-command-store'
import { isContentEmpty } from '@/utils/stringUtils'

var baseNoteContent = ref('') // Store the base content with raw commands
var realtimeTranscript = ref('') // Store real-time transcript
var noteTitle = ref('Ma nouvelle note') // Store the note title with default value
var titleError = ref(false) // Track title validation error
var contentError = ref(false) // Track content validation error

// Timer variables
const timeMaxValue = 25 // 25 seconds countdown
var recordingTimer = ref(timeMaxValue) // 25 seconds countdown
var timerInterval = ref<number | null>(null)

// Dynamic speech commands from database
const speechCommands = computed(() => {
  return commandStore.commands.map((command) => ({
    command_vocal: Array.isArray(command.command_vocal)
      ? command.command_vocal
      : [command.command_vocal],
    htmlTagStart: command.html_tag_start || '',
    htmlTagEnd: command.html_tag_end || '',
    isLineBreak:
      command.html_tag_end === '</br>' ||
      command.html_tag_start === '<br>' ||
      command.html_tag_start === '<br/>',
  }))
})

// Function to process speech commands for display only
const processSpeechCommands = (text: string): string => {
  if (!text.trim()) return text

  const commands = speechCommands.value
  if (commands.length === 0) return text

  // Create regex pattern from all commands (flatten arrays)
  const commandPatterns = commands.flatMap((cmd) => cmd.command_vocal).join('|')
  const regex = new RegExp(`(${commandPatterns})\\s+(.+?)(?=\\s+(${commandPatterns})|$)`, 'gi')

  let processedText = text
  let result = ''
  let lastIndex = 0

  // Process each command match
  processedText.replace(regex, (match, command, content, nextCommand, offset) => {
    // Add any text before this command
    if (offset > lastIndex) {
      result += text.substring(lastIndex, offset)
    }

    // Find the matching command configuration
    const commandConfig = commands.find((cmd) =>
      cmd.command_vocal.some((v) => v.toLowerCase() === command.toLowerCase()),
    )

    if (commandConfig) {
      const trimmedContent = content.trim()
      const capitalizedContent = trimmedContent.charAt(0).toUpperCase() + trimmedContent.slice(1)

      if (commandConfig.isLineBreak) {
        // Handle line break command
        result += `${capitalizedContent}<br>\n`
      } else if (commandConfig.htmlTagStart === '<ul>') {
        // Handle bullet list processing
        result += processBulletList(capitalizedContent)
      } else if (commandConfig.htmlTagStart && commandConfig.htmlTagEnd) {
        // Handle commands with HTML tags
        result += `${commandConfig.htmlTagStart}${capitalizedContent}${commandConfig.htmlTagEnd}\n`
      } else if (commandConfig.htmlTagStart) {
        // Handle self-closing tags like <br>
        result += `${commandConfig.htmlTagStart}${capitalizedContent}\n`
      } else {
        // Default: just add the content
        result += `${capitalizedContent}\n`
      }
    } else {
      // If no command found, add the original match
      result += match
    }

    lastIndex = offset + match.length
    return match
  })

  // Add any remaining text
  if (lastIndex < text.length) {
    result += text.substring(lastIndex)
  }

  return result.trim()
}

// Function to process bullet list content
const processBulletList = (content: string): string => {
  // Split content by "stop" to create list items
  const parts = content.split(/\s+stop\s+/i)
  let result = '<ul>\n'

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i].trim()
    if (!part) continue

    // Check if this part contains any command that would end the list
    const commands = speechCommands.value
    const commandPatterns = commands.flatMap((cmd) => cmd.command_vocal).join('|')
    const commandRegex = new RegExp(`\\b(${commandPatterns})\\b`, 'i')

    const commandMatch = part.match(commandRegex)

    if (commandMatch) {
      // Found a command in this part
      const commandIndex = part.toLowerCase().indexOf(commandMatch[0].toLowerCase())
      const beforeCommand = part.substring(0, commandIndex).trim()
      const fromCommand = part.substring(commandIndex).trim()

      // Add the part before the command as a list item if it exists
      if (beforeCommand) {
        result += `  <li>${beforeCommand}</li>\n`
      }

      // Close the list
      result += '</ul>\n'

      // Process the command part normally using the main processing function
      if (fromCommand) {
        result += processSpeechCommands(fromCommand) + '\n'
      }

      break
    } else {
      // Regular list item (no command found)
      result += `  <li>${part}</li>\n`
    }
  }

  // If we didn't encounter any command, close the list normally
  if (
    !parts.some((part) => {
      const commands = speechCommands.value
      const commandPatterns = commands.flatMap((cmd) => cmd.command_vocal).join('|')
      const commandRegex = new RegExp(`\\b(${commandPatterns})\\b`, 'i')
      return commandRegex.test(part)
    })
  ) {
    result += '</ul>\n'
  }

  return result
}

// Raw content with commands (for storage/editing)
const noteContent = computed({
  get: () => {
    console.log('Combining base content and real-time transcript')
    const base = baseNoteContent.value || ''
    const realtime = realtimeTranscript.value
    if (realtime && base) {
      const separator = base.endsWith(' ') ? '' : ' '
      return base + separator + realtime
    }
    return base + realtime
  },
  set: (value) => {
    console.log('Setting note content:', value)
    baseNoteContent.value = value
    realtimeTranscript.value = ''
  },
})

// Processed content for display (with commands converted to HTML)
const displayContent = computed({
  get: () => {
    return processSpeechCommands(noteContent.value)
  },
  set: (value) => {
    // When user edits manually, update the raw content directly
    noteContent.value = value
  },
})

// Google Speech service setup
const speechService = ref<GoogleSpeechService | null>(null)
const microphonePermission = ref<boolean | null>(null)
const isProcessing = ref(false)

const toast = useToast()
const speakerNoteStore = useSpeakerNoteStore()
const recordingStore = useRecordingStore()
const commandStore = useSpeakerCommandStore()
const isInitialized = ref(false)

// Initialize Google Speech service
const initSpeechService = () => {
  speechService.value = new GoogleSpeechService()
  console.log('Google Speech Service initialized : ', speechService.value)
}

// Handle recording state changes
const handleRecordingState = async (isRecording: boolean) => {
  // Prevent handling during initial component mount
  if (!isInitialized.value) return

  console.log('Recording status changed:', isRecording)
  if (isRecording) {
    // Starting to record
    if (microphonePermission.value === null) {
      const hasPermission = await requestMicrophonePermission()
      if (!hasPermission) return
    }

    if (microphonePermission.value) {
      await startRecording()
      startTimer() // Start the countdown timer
    }
  } else {
    // Stopping recording
    await stopRecording()
    stopTimer() // Stop the countdown timer
  }
}

const requestMicrophonePermission = async () => {
  if (!speechService.value) return false

  try {
    const hasPermission = await speechService.value.requestMicrophonePermission()
    microphonePermission.value = hasPermission

    if (hasPermission) {
      toast.add({
        severity: 'success',
        summary: 'Microphone autorisé',
        detail: 'Vous pouvez maintenant dicter vos notes',
        life: 3000,
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Microphone refusé',
        detail: "L'application ne peut pas fonctionner sans accès au microphone",
        life: 5000,
      })
    }

    return hasPermission
  } catch (error) {
    microphonePermission.value = false
    toast.add({
      severity: 'error',
      summary: 'Erreur microphone',
      detail: "Impossible d'accéder au microphone",
      life: 5000,
    })
    return false
  }
}

const startRecording = async () => {
  if (!speechService.value || !microphonePermission.value) return

  try {
    isProcessing.value = true

    // Set up real-time transcript callback
    speechService.value.setTranscriptCallback((transcript) => {
      realtimeTranscript.value = transcript
    })

    const stream = await speechService.value.startRecording()

    if (!stream) {
      throw new Error("Impossible de démarrer l'enregistrement")
    }

    toast.add({
      severity: 'info',
      summary: 'Enregistrement démarré',
      detail: 'Parlez maintenant...',
      life: 2000,
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: "Erreur d'enregistrement",
      detail: "Impossible de démarrer l'enregistrement",
      life: 5000,
    })
  } finally {
    isProcessing.value = false
  }
}

const stopRecording = async () => {
  if (!speechService.value) return

  try {
    isProcessing.value = true

    toast.add({
      severity: 'info',
      summary: 'Traitement en cours',
      detail: 'Transcription de votre audio...',
      life: 3000,
    })

    const transcript = await speechService.value.stopRecording()

    if (transcript || realtimeTranscript.value) {
      // Combine final transcript with any remaining real-time content
      const finalTranscript = transcript || realtimeTranscript.value
      const currentContent = baseNoteContent.value || ''
      const separator = currentContent && !currentContent.endsWith(' ') ? ' ' : ''
      baseNoteContent.value = currentContent + separator + finalTranscript
      realtimeTranscript.value = '' // Clear real-time transcript

      toast.add({
        severity: 'success',
        summary: 'Transcription terminée',
        detail: 'Texte ajouté à votre note',
        life: 3000,
      })
    } else {
      toast.add({
        severity: 'warn',
        summary: 'Aucun audio détecté',
        detail: "Aucun texte n'a pu être transcrit",
        life: 3000,
      })
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Erreur de transcription',
      detail: "Impossible de transcrire l'audio",
      life: 5000,
    })
  } finally {
    isProcessing.value = false
  }
}

const startTimer = () => {
  recordingTimer.value = timeMaxValue
  timerInterval.value = setInterval(() => {
    recordingTimer.value--
    if (recordingTimer.value <= 0) {
      // Timer reached 0, stop recording automatically
      handleTimeoutStop()
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  recordingTimer.value = timeMaxValue
}

const handleTimeoutStop = () => {
  stopTimer()

  // Show timeout toast
  toast.add({
    severity: 'warn',
    summary: 'Timeout atteint',
    detail: `Enregistrement arrêté automatiquement après ${timeMaxValue} secondes`,
    life: 4000,
  })

  // Stop recording using store
  recordingStore.stopRecording()
}

// Watch for recording changes from store
watch(
  () => recordingStore.isRecording,
  (newValue) => handleRecordingState(newValue),
)

onMounted(async () => {
  initSpeechService()
  // Fetch speaker commands from database
  await commandStore.fetchAllCommandsFromStore()
  // Mark as initialized after setup
  isInitialized.value = true
})

// Cleanup on unmount
onUnmounted(() => {
  if (speechService.value && speechService.value.getRecordingStatus()) {
    speechService.value.stopRecording()
  }
  stopTimer() // Clean up timer
})

const saveNote = async () => {
  let hasErrors = false

  // Validate title
  if (!noteTitle.value || noteTitle.value.trim().length === 0) {
    titleError.value = true
    hasErrors = true
  } else {
    titleError.value = false
  }

  // Validate content - check for meaningful text, not just HTML tags
  if (isContentEmpty(noteContent.value)) {
    contentError.value = true
    hasErrors = true
  } else {
    contentError.value = false
  }

  // Show error if validation fails
  if (hasErrors) {
    let errorMessage = 'Veuillez corriger les erreurs suivantes :'
    if (titleError.value && contentError.value) {
      errorMessage += '\n• Titre requis\n• Contenu requis'
    } else if (titleError.value) {
      errorMessage += '\n• Titre requis'
    } else if (contentError.value) {
      errorMessage += '\n• Contenu requis'
    }

    toast.add({
      severity: 'warn',
      summary: 'Champs requis',
      detail: errorMessage,
      life: 4000,
    })
    return
  }

  try {
    // Use the processed content (with HTML formatting) for saving
    const processedContent = processSpeechCommands(noteContent.value)
    console.log('Saving note with processed content:', processedContent)

    await speakerNoteStore.createNoteFromStore(noteTitle.value.trim(), processedContent, [])

    console.log('Note saved successfully:', speakerNoteStore.hasError)
    if (!speakerNoteStore.hasError) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Note saved successfully!',
        life: 3000,
      })
      // Clear the note content and reset title after saving
      clearNote()
    }
  } catch (error) {
    console.error('Error saving note:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save note. Please try again.',
      life: 5000,
    })
  } finally {
    speakerNoteStore.clearError()
  }
}

const clearNote = () => {
  noteContent.value = ''
  baseNoteContent.value = ''
  realtimeTranscript.value = ''
  noteTitle.value = 'Ma nouvelle note' // Reset title to default
  titleError.value = false // Clear title error
  contentError.value = false // Clear content error
  toast.add({
    severity: 'info',
    summary: 'Cleared',
    detail: 'Note cleared successfully!',
    life: 3000,
  })
}

// Clear title error when user starts typing
const onTitleInput = () => {
  if (titleError.value && noteTitle.value && noteTitle.value.trim().length > 0) {
    titleError.value = false
  }
}

// Clear content error when user starts typing
const onContentChange = () => {
  if (contentError.value && !isContentEmpty(noteContent.value)) {
    contentError.value = false
  }
}
</script>

<template>
  <Toast />

  <!-- Title Input -->
  <div class="title-section">
    <label for="note-title" class="title-label">
      <i class="pi pi-file-edit"></i>
      Titre de la note:
    </label>
    <InputText
      id="note-title"
      v-model="noteTitle"
      placeholder="Entrez le titre de votre note"
      class="title-input"
      :class="{ 'title-error': titleError }"
      @input="onTitleInput"
    />
  </div>

  <Editor
    v-model="displayContent"
    editorStyle="font-size: 1.25rem"
    class="note-text"
    :class="{ 'content-error': contentError }"
    @text-change="onContentChange"
  >
    <template v-slot:toolbar>
      <span class="ql-formats">
        <button v-tooltip.bottom="'Header 1'" class="ql-header" value="1"></button>
        <button v-tooltip.bottom="'Header 2'" class="ql-header" value="2"></button>
      </span>
      <span class="ql-formats">
        <button v-tooltip.bottom="'Bullet List'" class="ql-list" value="ordered"></button>
        <button v-tooltip.bottom="'Bullet List'" class="ql-list" value="bullet"></button>
      </span>
    </template>
  </Editor>

  <!-- Speech recognition status -->
  <div v-if="recordingStore.isRecording || isProcessing" class="speech-status">
    <span v-if="isProcessing" class="processing-indicator"> ⏳ Traitement en cours... </span>
    <span
      v-else-if="recordingStore.isRecording && microphonePermission"
      class="listening-indicator"
    >
      🎤 Enregistrement en cours...
    </span>
    <span v-else-if="microphonePermission === false" class="mic-denied">
      ❌ Microphone refusé - L'application ne peut pas fonctionner
    </span>
    <span v-else class="mic-waiting"> ⏳ Initialisation du microphone... </span>
  </div>

  <div class="buttons-display">
    <!-- Timer display when recording -->
    <div v-if="recordingStore.isRecording" class="timer-display">
      <i class="pi pi-clock"></i>
      <span :class="{ 'timer-warning': recordingTimer <= 10 }"> {{ recordingTimer }}s </span>
    </div>

    <Button
      class="p-button-secondary"
      icon="pi pi-times"
      label="Clear"
      severity="info"
      @click="clearNote()"
      :disabled="isProcessing || recordingStore.isRecording"
    />
    <Button
      class="p-button-secondary"
      icon="pi pi-check"
      label="Save Note"
      severity="success"
      @click="saveNote()"
      :disabled="isProcessing || recordingStore.isRecording"
    />
  </div>
</template>

<style scoped>
.title-section {
  margin-bottom: 1rem;
}

.title-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.title-label i {
  font-size: 0.875rem;
  color: var(--primary-color);
}

.title-input {
  width: 100%;
  font-size: 1.1rem;
  font-weight: 500;
}

.title-input.title-error {
  border-color: #ef4444;
  box-shadow: 0 0 0 1px #ef4444;
}

.title-input.title-error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

.note-text {
  font-size: 1.25rem;
  min-width: 50vw;
}

.note-text.content-error :deep(.ql-editor) {
  border-color: #ef4444;
  box-shadow: 0 0 0 1px #ef4444;
}

.note-text.content-error :deep(.ql-toolbar) {
  border-color: #ef4444;
}

.buttons-display {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 1rem;
  gap: 1rem;
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--surface-100);
  border: 1px solid var(--surface-300);
  border-radius: 0.375rem;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  font-size: 1rem;
  color: var(--text-color);
}

.timer-display i {
  color: var(--primary-color);
}

.timer-warning {
  color: #ef4444 !important;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* ...existing code... */

.processing-indicator {
  color: #f59e0b;
  font-weight: 500;
}

/* Add any additional styles for speech status indicators */
.speech-status {
  margin-top: 1rem;
  text-align: center;
}

.listening-indicator {
  color: #4caf50;
  font-weight: 500;
}

.mic-denied {
  color: #f44336;
  font-weight: 500;
}

.mic-waiting {
  color: #2196f3;
  font-weight: 500;
}
</style>
