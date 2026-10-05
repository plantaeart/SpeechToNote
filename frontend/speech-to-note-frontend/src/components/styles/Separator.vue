<script setup lang="ts">
// Type-based props: the compiler forbids referencing outer constants in an
// object-style `default`, so the fallback lives with the type instead.
withDefaults(
  defineProps<{
    height?: string
  }>(),
  {
    height: '4rem',
  },
)
</script>

<template>
  <div class="separator" :style="{ height }"></div>
</template>

<style scoped>
.separator {
  width: 100%;
}
</style>