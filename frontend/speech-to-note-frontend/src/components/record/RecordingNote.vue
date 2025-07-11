<script setup lang="ts">
import Separator from '../styles/Separator.vue'
import RecapCommands from './components/command-list/RecapCommands.vue'
import RecordButton from './components/record-button/RecordButton.vue'
import NoteDisplay from './components/note/NoteDisplay.vue'
</script>

<template>
  <div class="recording-note">
    <RecapCommands />
    <Separator :height="'2rem'" />
    <div class="record-note-content">
      <RecordButton />
      <NoteDisplay />
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
