<script setup lang="ts">
const height = '4rem' // Default height for the separator

const props = defineProps({
  height: {
    type: String,
    default: height,
  },
})
</script>

<template>
  <div class="separator" :style="{ height: props.height }"></div>
</template>

<style scoped></style>
