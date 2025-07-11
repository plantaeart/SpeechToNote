<script setup lang="ts">
import HeroHeader from './components/HeroHeader.vue'
import VocalCommandList from './components/VocalCommandList.vue'
import Footer from './components/Footer.vue'
import RecordingNote from './components/record/RecordingNote.vue'
import Separator from './components/styles/Separator.vue'
import NoteList from './components/NoteList.vue'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { useSpeakerNoteStore } from './stores/speaker-note-store'
import { useSpeakerCommandStore } from './stores/speaker-command-store'
import { computed, watch } from 'vue'

const noteStore = useSpeakerNoteStore()
const commandStore = useSpeakerCommandStore()

const toast = useToast()

// Watch for errors from store and display as toast
watch(
  () => noteStore.error,
  (newError) => {
    if (newError) {
      toast.add({
        severity: 'error',
        summary: 'Erreur',
        detail: 'Speaker Note error : ' + newError,
        life: 5000,
      })
    }
  },
)

watch(
  () => commandStore.error,
  (newError) => {
    if (newError) {
      toast.add({
        severity: 'error',
        summary: 'Erreur',
        detail: 'Speaker Command error : ' + newError,
        life: 5000,
      })
    }
  },
)
</script>

<template>
  <header></header>

  <main>
    <Toast />
    <HeroHeader />
    <Separator :height="'1rem'" />
    <RecordingNote />
    <Separator />
    <NoteList />
    <Separator />
    <VocalCommandList />
    <Separator />
    <Footer />
  </main>
</template>

<style scoped></style>
