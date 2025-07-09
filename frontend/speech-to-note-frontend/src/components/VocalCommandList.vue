<script setup lang="ts">
import { useSpeakerCommandStore } from '@/stores/speaker-command-store'
import { ref, onMounted, computed, nextTick } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import Divider from 'primevue/divider'
import ConfirmPopup from 'primevue/confirmpopup'
import { useConfirm } from 'primevue/useconfirm'
import { IS_DEBUG } from '@/config/env.current'
import { formatDate } from '@/utils/dateUtils'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import FloatingLoader from './FloatingLoader.vue'

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

// Local state for inline editing
const editingCommand = ref<number | null>(null)
const editCommandData = ref({
  command_name: '',
  command_vocal: '',
  command_description: '',
})

// Local state for creating new commands
const creatingCommand = ref(false)
const createCommandData = ref({
  command_name: '',
  command_vocal: '',
  command_description: '',
})

// Validation state
const createValidationErrors = ref({
  command_name: false,
  command_vocal: false,
})

// Validation state for update
const updateValidationErrors = ref({
  command_name: false,
  command_vocal: false,
})

// Scroll position preservation
const scrollPosition = ref(0)

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

const startEdit = (command: any) => {
  // Save current scroll position
  scrollPosition.value = window.scrollY

  editingCommand.value = command.id_command
  editCommandData.value = {
    command_name: command.command_name,
    command_vocal: command.command_vocal,
    command_description: command.command_description || '',
  }
}

const saveEdit = async () => {
  if (editingCommand.value) {
    // Validate required fields
    updateValidationErrors.value.command_name = !editCommandData.value.command_name.trim()
    updateValidationErrors.value.command_vocal = !editCommandData.value.command_vocal.trim()

    if (!updateValidationErrors.value.command_name && !updateValidationErrors.value.command_vocal) {
      await commandStore.updateCommandFromStore(editingCommand.value, {
        command_name: editCommandData.value.command_name,
        command_vocal: editCommandData.value.command_vocal,
        command_description: editCommandData.value.command_description,
      })
      editingCommand.value = null

      // Restore scroll position after DOM update
      await nextTick()
      window.scrollTo(0, scrollPosition.value)
    }
  }
}

const cancelEdit = () => {
  editingCommand.value = null
  editCommandData.value = {
    command_name: '',
    command_vocal: '',
    command_description: '',
  }
  // Reset validation errors
  updateValidationErrors.value.command_name = false
  updateValidationErrors.value.command_vocal = false

  // Restore scroll position after DOM update
  nextTick(() => {
    window.scrollTo(0, scrollPosition.value)
  })
}

const startCreate = () => {
  scrollPosition.value = window.scrollY
  creatingCommand.value = true
  createCommandData.value = {
    command_name: '',
    command_vocal: '',
    command_description: '',
  }
}

const saveCreate = async () => {
  // Validate required fields
  createValidationErrors.value.command_name = !createCommandData.value.command_name.trim()
  createValidationErrors.value.command_vocal = !createCommandData.value.command_vocal.trim()

  if (!createValidationErrors.value.command_name && !createValidationErrors.value.command_vocal) {
    await commandStore.createCommandFromStore(
      createCommandData.value.command_name,
      createCommandData.value.command_vocal,
      createCommandData.value.command_description,
    )
    creatingCommand.value = false

    await nextTick()
    window.scrollTo(0, scrollPosition.value)
  }
}

const cancelCreate = () => {
  creatingCommand.value = false
  createCommandData.value = {
    command_name: '',
    command_vocal: '',
    command_description: '',
  }
  // Reset validation errors
  createValidationErrors.value.command_name = false
  createValidationErrors.value.command_vocal = false

  nextTick(() => {
    window.scrollTo(0, scrollPosition.value)
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

    <!-- Commands Grid - always show when we have commands -->
    <div class="commands-grid">
      <!-- Empty state when no commands -->
      <Card v-if="!hasCommands && !isLoading" class="empty-state-card">
        <template #content>
          <div class="empty-state">
            <i class="pi pi-microphone empty-icon"></i>
            <h3>Aucune commande vocale</h3>
          </div>
        </template>
      </Card>

      <!-- Existing Commands -->
      <Card
        v-if="hasCommands"
        v-for="command in commands.sort((a, b) => a.id_command - b.id_command)"
        :key="command.id_command"
        class="command-card"
        :class="{ editing: editingCommand === command.id_command }"
      >
        <template #header>
          <div class="command-header">
            <div class="command-name-section">
              <i class="pi pi-volume-up command-icon"></i>
              <h3 v-if="editingCommand !== command.id_command">{{ command.command_name }}</h3>
              <InputText
                v-else
                v-model="editCommandData.command_name"
                class="edit-title-input"
                placeholder="Nom de la commande"
                :invalid="updateValidationErrors.command_name"
              />
            </div>
            <div class="command-actions">
              <!-- Edit Mode Actions -->
              <template v-if="editingCommand === command.id_command">
                <Button
                  @click="saveEdit"
                  icon="pi pi-check"
                  severity="success"
                  text
                  rounded
                  size="medium"
                  :title="'Sauvegarder'"
                />
                <Button
                  @click="cancelEdit"
                  icon="pi pi-times"
                  severity="secondary"
                  text
                  rounded
                  size="medium"
                  :title="'Annuler'"
                />
              </template>
              <!-- Normal Mode Actions -->
              <template v-else>
                <Button
                  @click="startEdit(command)"
                  icon="pi pi-pencil"
                  severity="info"
                  text
                  rounded
                  size="medium"
                  :title="'Modifier'"
                />
                <Button
                  @click="(event) => deleteCommand(event, command.id_command, command.command_name)"
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  rounded
                  size="medium"
                  :title="'Supprimer'"
                />
              </template>
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
              <Tag
                v-if="editingCommand !== command.id_command"
                :value="command.command_vocal"
                severity="info"
                class="vocal-tag"
              />
              <InputText
                v-else
                v-model="editCommandData.command_vocal"
                class="edit-vocal-input"
                placeholder="Déclencheur vocal"
                :invalid="updateValidationErrors.command_vocal"
              />
            </div>

            <!-- Description -->
            <div class="description-section">
              <label class="field-label">
                <i class="pi pi-info-circle"></i>
                Description:
              </label>
              <p
                v-if="editingCommand !== command.id_command && command.command_description"
                class="description-text"
              >
                {{ command.command_description }}
              </p>
              <p
                v-else-if="editingCommand !== command.id_command && !command.command_description"
                class="description-text empty"
              >
                Aucune description
              </p>
              <Textarea
                v-else
                v-model="editCommandData.command_description"
                rows="3"
                class="edit-description-input"
                placeholder="Description (optionnelle)"
              />
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

      <!-- Create Command Card -->
      <Card class="command-card create-card" :class="{ editing: creatingCommand }">
        <template #header>
          <div class="command-header">
            <div class="command-name-section">
              <InputText
                v-if="creatingCommand"
                v-model="createCommandData.command_name"
                class="edit-title-input"
                placeholder="Nom de la commande"
                :invalid="createValidationErrors.command_name"
              />
            </div>
            <div class="command-actions">
              <!-- Create Mode Actions -->
              <template v-if="creatingCommand">
                <Button
                  @click="saveCreate"
                  icon="pi pi-check"
                  severity="success"
                  text
                  rounded
                  size="medium"
                  :title="'Créer'"
                />
                <Button
                  @click="cancelCreate"
                  icon="pi pi-times"
                  severity="secondary"
                  text
                  rounded
                  size="medium"
                  :title="'Annuler'"
                />
              </template>
            </div>
          </div>
        </template>

        <template #content>
          <div class="command-content">
            <div v-if="!creatingCommand" class="create-button-content">
              <Button
                @click="startCreate"
                icon="pi pi-plus"
                label="Créer une commande"
                severity="success"
                outlined
                class="create-button-display"
              />
            </div>
            <div v-else>
              <!-- Vocal Trigger -->
              <div class="vocal-trigger-section">
                <label class="field-label">
                  <i class="pi pi-comment"></i>
                  Déclencheur vocal:
                </label>
                <InputText
                  v-model="createCommandData.command_vocal"
                  class="edit-vocal-input"
                  placeholder="Déclencheur vocal"
                  :invalid="createValidationErrors.command_vocal"
                />
              </div>

              <!-- Description -->
              <div class="description-section">
                <label class="field-label">
                  <i class="pi pi-info-circle"></i>
                  Description:
                </label>
                <Textarea
                  v-model="createCommandData.command_description"
                  rows="3"
                  class="edit-description-input"
                  placeholder="Description (optionnelle)"
                />
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Floating loader component -->
    <FloatingLoader
      :visible="isLoading || refreshing"
      position="bottom-right"
      size="medium"
      message="Chargement..."
    />

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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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

.editing {
  border: 2px solid var(--primary-color);
  box-shadow: 0 0 10px rgba(var(--primary-color-rgb), 0.3);
}

.edit-title-input {
  flex: 1;
  font-size: 1.25rem;
  font-weight: 600;
  width: 100%;
}

.edit-vocal-input,
.edit-description-input {
  width: 100%;
  margin-top: 0.5rem;
}

.description-text.empty {
  color: var(--text-color-secondary);
  font-style: italic;
}

.command-actions {
  display: flex;
  gap: 0.25rem;
}

.create-card {
  border: 2px dashed var(--surface-border);
  background: var(--surface-50);
}

.create-card:hover {
  border-color: var(--primary-color);
  background: var(--surface-100);
}

.create-button-display {
  width: 100%;
  min-height: 15vw;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  font-size: 1rem;
}

.create-button-content {
  text-align: center;
}

/* Make sure input fields are properly styled */
.edit-title-input:deep(.p-inputtext) {
  font-size: 1.25rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
}

.edit-vocal-input:deep(.p-inputtext) {
  font-family: 'Courier New', monospace;
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
