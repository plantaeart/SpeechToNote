<script setup lang="ts">
import HeroHeader from './components/HeroHeader.vue'
import VocalCommandList from './components/VocalCommandList.vue'
import Footer from './components/Footer.vue'
import RecordingNote from './components/record/RecordingNote.vue'
import Separator from './components/styles/Separator.vue'
</script>

<template>
  <header></header>

  <main>
    <HeroHeader />
    <Separator :height="'1rem'" />
    <RecordingNote />
    <Separator />
    <VocalCommandList />
    <Separator />
    <Footer />
  </main>
</template>

<style scoped></style>
