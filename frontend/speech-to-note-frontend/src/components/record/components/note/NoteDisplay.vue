<script setup lang="ts">
import { ref } from 'vue'
import NoteContent from './note-content/NoteContent.vue'
import { useRecordingStore } from '@/stores/recording-store'

const recordingStore = useRecordingStore()
</script>

<template>
  <div class="note-content">
    <div>
      <h2>Recording Note</h2>
      <NoteContent />
    </div>
  </div>
</template>

<style scoped>
.not-recording {
  color: var(--beige-color);
  font-size: 2.5rem;
  font-weight: bold;
  width: 50vw;
}

.note-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  margin-left: 1rem;
}
</style>
