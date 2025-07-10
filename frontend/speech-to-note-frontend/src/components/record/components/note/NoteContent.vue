<script setup lang="ts">
import Editor from 'primevue/editor'
import { ref, watch } from 'vue'

var noteContent = ref('')
const emit = defineEmits(['noteContentStatus'])
watch(noteContent, (newValue) => {
  emit('noteContentStatus', newValue)
})
</script>

<template>
  <Editor v-model="noteContent" editorStyle="font-size: 1.25rem" class="note-text">
    <template v-slot:toolbar>
      <span class="ql-formats">
        <button v-tooltip.bottom="'Header'" class="ql-header" value="1"></button>
        <button v-tooltip.bottom="'Header'" class="ql-header" value="2"></button>
        <button class="ql-list" value="bullet"></button>
      </span>
    </template>
  </Editor>
</template>

<style scoped>
.note-text {
  font-size: 1.25rem;
  min-width: 60vw;
}
</style>
