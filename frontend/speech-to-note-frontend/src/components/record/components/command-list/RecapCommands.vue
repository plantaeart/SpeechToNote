<script setup lang="ts">
import { computed } from 'vue'
import { useSpeakerCommandStore } from '@/stores/speaker-command-store'
import { Tag } from 'primevue'

const commandStore = useSpeakerCommandStore()
const commands = computed(() => commandStore.sortedCommands)
</script>

<template>
  <div class="recap-commands">
    <h2><u>Commands recap</u></h2>
    <div v-if="commands.length > 0" class="commands-list">
      <div class="command-display" v-for="(command, index) in commands" :key="index">
        <div class="command-item">
          <h3 class="command-name-text">{{ command.command_name }}</h3>
          <Tag class="command-vocal-text">{{ command.command_vocal }}</Tag>
        </div>
        <div v-if="index < commands.length - 1" class="command-vertical-separator" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.commands-list {
  display: flex;
  flex-direction: row;
  width: 100%;
}

.command-display {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.command-vertical-separator {
  width: 1px;
  background-color: var(--beige-color);
  height: 50%;
  margin: 0 1rem 0 1rem;
}

.command-vocal-text {
  width: max-content;
}

.command-name-text {
  width: max-content;
  color: var(--beige-color);
}
</style>
