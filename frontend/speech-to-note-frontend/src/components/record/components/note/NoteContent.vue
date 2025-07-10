<script setup lang="ts">
import Editor from 'primevue/editor'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import { ref, watch } from 'vue'
import { useToast } from 'primevue/usetoast'

var noteContent = ref('')
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
  noteContent.value = ''
  console.log('Note cleared')
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
</style>
