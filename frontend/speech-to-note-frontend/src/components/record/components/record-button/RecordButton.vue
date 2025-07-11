<script setup lang="ts">
import { Button } from 'primevue'
import { ref, watch } from 'vue'

var isRecording = ref(false)
const startRecording = () => {
  // Logic to start recording goes here
  isRecording.value = !isRecording.value
}

// Emit isRecording value to parent component
const emit = defineEmits(['recordingStatus'])
watch(isRecording, (newValue) => {
  emit('recordingStatus', newValue)
})
</script>

<template>
  <div class="button-content">
    <Button
      class="mic-button"
      icon="pi pi-microphone"
      v-on:click="startRecording()"
      :class="isRecording ? 'p-button-danger button-pulse-animation' : 'p-button-success'"
    />
  </div>
</template>

<style scoped>
.button-content {
  display: flex;
  justify-content: center;
  align-items: center;
}

.mic-button {
  width: 20rem;
  height: 20rem;
  border-radius: 50%;
}

.mic-button:deep(.p-button-icon) {
  font-size: 10rem;
}

.button-pulse-animation {
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
</style>
