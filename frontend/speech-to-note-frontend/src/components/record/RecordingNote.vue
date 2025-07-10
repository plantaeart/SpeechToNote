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
    <Separator :height="'2rem'" />
    <div class="record-note-content">
      <RecordButton @recordingStatus="isRecording = $event" />
      <NoteContent :isRecording="isRecording" />
    </div>
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

.recording-note .record-note-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: auto;
}
</style>
