<script setup lang="ts">
import { ref } from 'vue'
import NoteContent from './note-content/NoteContent.vue'

const noteContent = ref('')
const props = defineProps<{
  isRecording: boolean
}>()
</script>

<template>
  <div class="note-content">
    <div v-if="props.isRecording || !['', '<p></p>'].includes(noteContent)">
      <h2>Recording Note</h2>
      <NoteContent :is-recording="props.isRecording" @noteContentStatus="noteContent = $event" />
    </div>
    <div v-else>
      <p class="not-recording">Not Recording</p>
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
