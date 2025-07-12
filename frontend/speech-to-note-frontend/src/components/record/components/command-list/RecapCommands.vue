<script setup lang="ts">
import { computed } from 'vue'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import { useSpeakerCommandStore } from '@/stores/speaker-command-store'

const commandStore = useSpeakerCommandStore()

// Reactive computed properties from store
const commands = computed(() => commandStore.sortedCommands)
const hasCommands = computed(() => commandStore.hasCommands)
</script>

<template>
  <div class="recap-commands">
    <Card class="commands-card">
      <template #header>
        <div class="commands-header">
          <div class="title-section">
            <i class="pi pi-microphone title-icon"></i>
            <h3>Commandes Vocales Disponibles</h3>
          </div>
        </div>
      </template>

      <template #content>
        <!-- Empty state -->
        <div v-if="!hasCommands" class="empty-state">
          <i class="pi pi-microphone empty-icon"></i>
          <p>Aucune commande vocale configurée</p>
        </div>

        <!-- Commands list -->
        <div v-else class="commands-list">
          <div
            v-for="(command, index) in commands"
            :key="command.id_command"
            class="command-display"
          >
            <span class="command-item">
              <span class="command-name">{{ command.command_name }}</span>
              <div>
                <Tag
                  v-for="(vocal, vocalIndex) in Array.isArray(command.command_vocal)
                    ? command.command_vocal
                    : [command.command_vocal]"
                  :key="vocalIndex"
                  :value="vocal"
                  severity="info"
                  class="vocal-tag"
                />
              </div>
            </span>
            <span v-if="index < commands.length - 1" class="separator">|</span>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.recap-commands {
  width: 100%;
}

.commands-card {
  width: 100%;
}

.commands-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  font-size: 1.25rem;
  color: var(--primary-color);
}

.commands-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.25rem;
  font-weight: 600;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: var(--text-color-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--text-color-secondary);
}

.command-display {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.commands-list {
  display: flex;
  flex-wrap: wrap;
  align-items: start;
  justify-content: center;
}

.command-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.command-name {
  font-weight: 600;
  color: var(--text-color);
}

.vocal-tag {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  margin-left: 0.25rem;
}

.separator {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-color-secondary);
  font-weight: 300;
  margin: 0 0.5rem;
  height: 5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .commands-header {
    text-align: center;
  }

  .command-line {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

/* Dark theme adjustments */
@media (prefers-color-scheme: dark) {
  .commands-header {
    background: var(--surface-100);
  }

  .command-item {
    background: var(--surface-100);
  }

  .command-item:hover {
    background: var(--surface-200);
  }
}
</style>
