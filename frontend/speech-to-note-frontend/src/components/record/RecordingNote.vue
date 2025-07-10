<script setup lang="ts">
import Separator from '../styles/Separator.vue'
import NoteContent from './components/note/NoteDisplay.vue'
import RecapCommands from './components/RecapCommands.vue'
import RecordButton from './components/RecordButton.vue'
import { ref } from 'vue'

const isRecording = ref(false)
</script>

<template>
  <div class="recording-note">
    <RecapCommands />
    <Separator :height="'1rem'" />
    <RecordButton @recordingStatus="isRecording = $event" />
    <Separator />
    <NoteContent :isRecording="isRecording" />
  </div>
</template>

<style scoped>
.recording-note {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: auto;
}
</style>
