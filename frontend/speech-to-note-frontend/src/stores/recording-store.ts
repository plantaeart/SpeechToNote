import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRecordingStore = defineStore('recording', () => {
  const isRecording = ref(false)

  const startRecording = () => {
    isRecording.value = true
  }

  const stopRecording = () => {
    isRecording.value = false
  }

  const toggleRecording = () => {
    isRecording.value = !isRecording.value
  }

  return {
    isRecording,
    startRecording,
    stopRecording,
    toggleRecording,
  }
})
