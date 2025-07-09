<script setup lang="ts">
import { useSpeakerCommandStore } from '@/stores/speaker-command-store'
import { ref, onMounted, computed } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import Divider from 'primevue/divider'
import ConfirmPopup from 'primevue/confirmpopup'
import { useConfirm } from 'primevue/useconfirm'
import { IS_DEBUG } from '@/config/env.current'
import { formatDate } from '@/utils/dateUtils'

const commandStore = useSpeakerCommandStore()
const confirm = useConfirm()

// Reactive computed properties from store
const commands = computed(() => commandStore.sortedCommands)
const isLoading = computed(() => commandStore.isLoading)
const hasError = computed(() => commandStore.hasError)
const error = computed(() => commandStore.error)
const hasCommands = computed(() => commandStore.hasCommands)

// Local state for refresh functionality
const refreshing = ref(false)

// Fetch commands on component mount
onMounted(async () => {
  await fetchCommands()
})

// Methods
const fetchCommands = async () => {
  refreshing.value = true
  try {
    await commandStore.fetchAllCommandsFromStore()
  } finally {
    refreshing.value = false
  }
}

const clearError = () => {
  commandStore.clearError()
}

const deleteCommand = async (event: Event, id_command: number, commandName: string) => {
  console.log(`Start deleting command with ID: ${id_command} - Name: ${commandName}`)
  confirm.require({
    target: event.currentTarget as HTMLElement,
    message: `Êtes-vous sûr de vouloir supprimer la commande "${commandName}" ?`,
    header: 'Confirmation de suppression',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Annuler',
    acceptLabel: 'Supprimer',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await commandStore.deleteCommandFromStore(id_command)
    },
  })
}
</script>

<template>
  <div class="vocal-command-list">
    <div class="header">
      <div class="title-section">
        <i class="pi pi-microphone title-icon"></i>
        <h2>Commandes Vocales</h2>
        <Badge
          v-if="hasCommands && IS_DEBUG"
          :value="commandStore.commandsCount"
          severity="info"
          class="commands-badge"
        />
      </div>

      <div class="actions">
        <Button
          @click="fetchCommands"
          :loading="isLoading || refreshing"
          icon="pi pi-refresh"
          label="Actualiser"
          size="medium"
          severity="success"
          outlined
        />
      </div>
    </div>

    <!-- Error Display -->
    <Message
      v-if="hasError"
      severity="error"
      :closable="true"
      @close="clearError"
      class="error-message"
    >
      {{ error }}
    </Message>

    <!-- Loading State -->
    <div v-if="isLoading && !refreshing" class="loading-container">
      <ProgressSpinner />
      <p class="loading-text">Chargement des commandes...</p>
    </div>

    <!-- Empty State -->
    <Card v-else-if="!hasCommands && !isLoading" class="empty-state-card">
      <template #content>
        <div class="empty-state">
          <i class="pi pi-microphone empty-icon"></i>
          <h3>Aucune commande vocale</h3>
          <p>Créez votre première commande vocale pour commencer.</p>
          <Button
            icon="pi pi-plus"
            label="Créer une commande"
            severity="success"
            class="create-btn"
          />
        </div>
      </template>
    </Card>

    <!-- Commands Grid -->
    <div v-else class="commands-grid">
      <Card
        v-for="command in commands.sort((a, b) => a.id_command - b.id_command)"
        :key="command.id_command"
        class="command-card"
      >
        <template #header>
          <div class="command-header">
            <div class="command-name-section">
              <i class="pi pi-volume-up command-icon"></i>
              <h3>{{ command.command_name }}</h3>
            </div>
            <div class="command-actions">
              <Button
                @click="(event) => deleteCommand(event, command.id_command, command.command_name)"
                icon="pi pi-trash"
                severity="danger"
                text
                rounded
                size="medium"
                :title="'Supprimer'"
              />
            </div>
          </div>
        </template>

        <template #content>
          <div class="command-content">
            <!-- Vocal Trigger -->
            <div class="vocal-trigger-section">
              <label class="field-label">
                <i class="pi pi-comment"></i>
                Déclencheur vocal:
              </label>
              <Tag :value="command.command_vocal" severity="info" class="vocal-tag" />
            </div>

            <!-- Description -->
            <div v-if="command.command_description" class="description-section">
              <label class="field-label">
                <i class="pi pi-info-circle"></i>
                Description:
              </label>
              <p class="description-text">{{ command.command_description }}</p>
            </div>

            <!-- Metadata -->
            <div v-if="IS_DEBUG">
              <Divider />
              <div class="metadata-section">
                <div class="meta-grid">
                  <div class="meta-item">
                    <span class="meta-label">
                      <i class="pi pi-hashtag"></i>
                      ID:
                    </span>
                    <Tag :value="command.id_command" severity="secondary" />
                  </div>

                  <div class="meta-item">
                    <span class="meta-label">
                      <i class="pi pi-calendar-plus"></i>
                      Créé:
                    </span>
                    <span class="meta-value">{{ formatDate(command.created_at) }}</span>
                  </div>

                  <div v-if="command.updated_at !== command.created_at" class="meta-item">
                    <span class="meta-label">
                      <i class="pi pi-calendar-times"></i>
                      Modifié:
                    </span>
                    <span class="meta-value">{{ formatDate(command.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- ConfirmPopup component -->
    <ConfirmPopup />
  </div>
</template>

<style scoped>
.vocal-command-list {
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.title-icon {
  font-size: 2rem;
  color: var(--primary-color);
}

.header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.75rem;
}

.commands-badge {
  margin-left: 0.5rem;
}

.error-message {
  margin-bottom: 1rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  gap: 1rem;
}

.loading-text {
  margin: 0;
  color: var(--text-color-secondary);
}

.empty-state-card {
  margin: 2rem 0;
}

.empty-state {
  text-align: center;
  padding: 2rem;
}

.empty-icon {
  font-size: 4rem;
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 1rem;
  color: var(--text-color);
}

.empty-state p {
  margin: 0 0 1.5rem;
  color: var(--text-color-secondary);
}

.commands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.command-card {
  background-color: var(--eerie-black-color);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.command-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow);
}

.command-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: var(--surface-50);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
}

.command-name-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.command-icon {
  font-size: 1.25rem;
  color: var(--primary-color);
}

.command-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.25rem;
  font-weight: 600;
}

.command-content {
  padding: 1rem;
}

.vocal-trigger-section,
.description-section {
  margin-bottom: 1.5rem;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.field-label i {
  font-size: 0.875rem;
}

.vocal-tag {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.description-text {
  margin: 0;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.metadata-section {
  margin-top: 1rem;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.meta-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}

.meta-label i {
  font-size: 0.7rem;
}

.meta-value {
  font-size: 0.75rem;
  color: var(--text-color);
}

.footer-stats {
  margin-top: 2rem;
}

.stats-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.5rem;
}

.stats-icon {
  font-size: 1.1rem;
  color: var(--primary-color);
}

.stats-text {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .commands-grid {
    grid-template-columns: 1fr;
  }

  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .title-section {
    justify-content: center;
  }

  .command-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .command-actions {
    align-self: flex-end;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }

  .meta-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

/* Dark theme adjustments */
@media (prefers-color-scheme: dark) {
  .command-header {
    background: var(--surface-100);
  }
}
</style>
