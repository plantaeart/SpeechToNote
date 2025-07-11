<script setup lang="ts">
import Editor from 'primevue/editor'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { GoogleSpeechService } from '@/services/GoogleSpeechService'

const props = defineProps<{
  isRecording: boolean
}>()

var baseNoteContent = ref('') // Store the base content
var realtimeTranscript = ref('') // Store real-time transcript

// Computed property to combine base content with real-time transcript
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

// Google Speech service setup
const speechService = ref<GoogleSpeechService | null>(null)
const microphonePermission = ref<boolean | null>(null)
const isProcessing = ref(false)

const emit = defineEmits(['noteContentStatus'])
watch(noteContent, (newValue) => {
  // Use regex to determine if newvalue is empty tags, if yes, newValue will be an empty string
  const emptyTagsRegex = /^(<p><br><\/p>|<p><\/p>|<br>|\s*)$/
  if (emptyTagsRegex.test(newValue)) {
    newValue = ''
    noteContent.value = newValue
  }
  emit('noteContentStatus', newValue)
})

const toast = useToast()

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

const saveNote = () => {
  // Logic to save the note goes here
  console.log('Note saved:', noteContent.value)
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Note saved successfully!',
    life: 3000,
  })
}

const clearNote = () => {
  baseNoteContent.value = ''
  realtimeTranscript.value = ''
  toast.add({
    severity: 'info',
    summary: 'Cleared',
    detail: 'Note cleared successfully!',
    life: 3000,
  })
}
</script>

<template>
  <Toast />
  <Editor v-model="noteContent" editorStyle="font-size: 1.25rem" class="note-text">
    <template v-slot:toolbar>
      <span class="ql-formats">
        <button v-tooltip.bottom="'Header'" class="ql-header" value="1"></button>
        <button v-tooltip.bottom="'Header'" class="ql-header" value="2"></button>
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
.note-text {
  font-size: 1.25rem;
  min-width: 50vw;
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
