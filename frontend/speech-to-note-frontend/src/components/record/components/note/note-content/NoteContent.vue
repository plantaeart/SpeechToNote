<script setup lang="ts">
import Editor from 'primevue/editor'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import InputText from 'primevue/inputtext'
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { GoogleSpeechService } from '@/services/GoogleSpeechService'
import { useSpeakerNoteStore } from '@/stores/speaker-note-store'
import { isContentEmpty } from '@/utils/stringUtils'

const props = defineProps<{
  isRecording: boolean
}>()

var baseNoteContent = ref('') // Store the base content with raw commands
var realtimeTranscript = ref('') // Store real-time transcript
var noteTitle = ref('Ma nouvelle note') // Store the note title with default value
var titleError = ref(false) // Track title validation error
var contentError = ref(false) // Track content validation error

// Function to process speech commands for display only
const processSpeechCommands = (text: string): string => {
  let processedText = text

  // Handle title commands - wrap following text in <h1> tags and add line break
  processedText = processedText.replace(
    /(nouveau titre|titre)\s+(.+?)(?=\s+(nouveau titre|titre|saut de ligne)|$)/gi,
    (match, command, titleText) => {
      // Capitalize first letter of the title and trim whitespace
      const trimmedTitle = titleText.trim()
      const capitalizedTitle = trimmedTitle.charAt(0).toUpperCase() + trimmedTitle.slice(1)
      return `<h1>${capitalizedTitle}</h1>\n`
    },
  )

  // Handle "Saut de ligne" command - add line break and process following text
  processedText = processedText.replace(
    /saut de ligne\s+(.+?)(?=\s+(nouveau titre|titre|saut de ligne)|$)/gi,
    (match, followingText) => {
      // Capitalize first letter of the paragraph and trim whitespace
      const trimmedText = followingText.trim()
      const capitalizedText = trimmedText.charAt(0).toUpperCase() + trimmedText.slice(1)
      return `${capitalizedText}\n`
    },
  )

  // Handle standalone "Saut de ligne" command (without following text)
  processedText = processedText.replace(/saut de ligne\s*$/gi, '\n')

  return processedText.trim()
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

// Initialize Google Speech service
const initSpeechService = () => {
  speechService.value = new GoogleSpeechService()
  console.log('Google Speech Service initialized : ', speechService.value)
}

// Handle recording state changes
const handleRecordingState = async (isRecording: boolean) => {
  console.log('Recording status changed:', isRecording)
  if (isRecording) {
    // Starting to record
    if (microphonePermission.value === null) {
      const hasPermission = await requestMicrophonePermission()
      if (!hasPermission) return
    }

    if (microphonePermission.value) {
      await startRecording()
    }
  } else {
    // Stopping recording
    await stopRecording()
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

// Watch for recording changes
watch(
  () => props.isRecording,
  (newValue) => handleRecordingState(newValue),
)

onMounted(async () => {
  initSpeechService()
  // Handle initial recording state
  await handleRecordingState(props.isRecording)
})

onUnmounted(() => {
  if (speechService.value?.getRecordingStatus()) {
    speechService.value.stopRecording()
  }
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
    console.log('Saving note with content:', noteContent.value)
    // Use the title from input and raw content for saving
    await speakerNoteStore.createNoteFromStore(noteTitle.value.trim(), noteContent.value, [])

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
        <button class="ql-header" value="1"></button>
        <button class="ql-header" value="2"></button>
      </span>
      <span class="ql-formats">
        <button class="ql-list" value="bullet"></button>
      </span>
    </template>
  </Editor>

  <!-- Speech recognition status -->
  <div v-if="props.isRecording || isProcessing" class="speech-status">
    <span v-if="isProcessing" class="processing-indicator"> ⏳ Traitement en cours... </span>
    <span v-else-if="props.isRecording && microphonePermission" class="listening-indicator">
      🎤 Enregistrement en cours...
    </span>
    <span v-else-if="microphonePermission === false" class="mic-denied">
      ❌ Microphone refusé - L'application ne peut pas fonctionner
    </span>
    <span v-else class="mic-waiting"> ⏳ Initialisation du microphone... </span>
  </div>

  <div class="buttons-display">
    <Button
      class="p-button-secondary"
      icon="pi pi-times"
      label="Clear"
      severity="info"
      @click="clearNote()"
      :disabled="isProcessing || props.isRecording"
    />
    <Button
      class="p-button-secondary"
      icon="pi pi-check"
      label="Save Note"
      severity="success"
      @click="saveNote()"
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
  justify-content: flex-end;
  margin-top: 1rem;
  gap: 1rem;
}

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
