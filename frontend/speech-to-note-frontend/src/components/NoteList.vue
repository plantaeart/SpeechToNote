<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Toast from 'primevue/toast'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import Divider from 'primevue/divider'
import ConfirmPopup from 'primevue/confirmpopup'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { IS_DEBUG } from '@/config/env.current'
import { formatDate } from '@/utils/dateUtils'
import InputText from 'primevue/inputtext'
import Editor from 'primevue/editor'
import FloatingLoader from './FloatingLoader.vue'
import { useSpeakerNoteStore } from '@/stores/speaker-note-store'
import { isContentEmpty } from '@/utils/stringUtils'

const noteStore = useSpeakerNoteStore()
const confirm = useConfirm()
const toast = useToast()

// Reactive computed properties from store
const notes = computed(() => noteStore.sortedNotes)
const isLoading = computed(() => noteStore.isLoading)
const hasNotes = computed(() => noteStore.hasNotes)

// Local state for refresh functionality
const refreshing = ref(false)

// Local state for inline editing
const editingNote = ref<number | null>(null)
const editNoteData = ref({
  title: '',
  content: '',
})
const editTitleError = ref(false)
const editContentError = ref(false)

// Scroll position preservation
const scrollPosition = ref(0)

// Fetch notes on component mount
onMounted(async () => {
  await fetchNotes()
})

// Methods
const fetchNotes = async () => {
  refreshing.value = true
  try {
    await noteStore.fetchAllNotesFromStore()
  } finally {
    refreshing.value = false
  }
}

const clearError = () => {
  noteStore.clearError()
}

const deleteNote = async (event: Event, id_note: number, noteTitle: string) => {
  console.log(`Start deleting note with ID: ${id_note} - Title: ${noteTitle}`)
  confirm.require({
    target: event.currentTarget as HTMLElement,
    message: `Êtes-vous sûr de vouloir supprimer la note "${noteTitle}" ?`,
    header: 'Confirmation de suppression',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Annuler',
    acceptLabel: 'Supprimer',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await noteStore.deleteNoteFromStore(id_note)
    },
  })
}

const cloneNote = async (event: Event, note: any) => {
  console.log(`Start cloning note with ID: ${note.id_note} - Title: ${note.title}`)
  const clonedTitle = `${note.title} (Copie)`
  confirm.require({
    target: event.currentTarget as HTMLElement,
    message: `Êtes-vous sûr de vouloir dupliquer la note "${note.title}" ?`,
    header: 'Confirmation de duplication',
    icon: 'pi pi-copy',
    rejectLabel: 'Annuler',
    acceptLabel: 'Dupliquer',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-warning',
    accept: async () => {
      await noteStore.createNoteFromStore(clonedTitle, note.content)
    },
  })
}

const startEdit = (note: any) => {
  // Save current scroll position
  scrollPosition.value = window.scrollY

  editingNote.value = note.id_note
  editNoteData.value = {
    title: note.title,
    content: note.content,
  }
  // Clear any previous errors
  editTitleError.value = false
  editContentError.value = false
}

const saveEdit = async () => {
  if (editingNote.value) {
    let hasErrors = false

    // Validate title
    if (!editNoteData.value.title || editNoteData.value.title.trim().length === 0) {
      editTitleError.value = true
      hasErrors = true
    } else {
      editTitleError.value = false
    }

    // Validate content - check for meaningful text, not just HTML tags
    if (isContentEmpty(editNoteData.value.content)) {
      editContentError.value = true
      hasErrors = true
    } else {
      editContentError.value = false
    }

    // Show error if validation fails
    if (hasErrors) {
      let errorMessage = 'Veuillez corriger les erreurs suivantes :'
      if (editTitleError.value && editContentError.value) {
        errorMessage += '\n• Titre requis\n• Contenu requis'
      } else if (editTitleError.value) {
        errorMessage += '\n• Titre requis'
      } else if (editContentError.value) {
        errorMessage += '\n• Contenu requis'
      }

      toast.add({
        severity: 'warn',
        summary: 'Champs requis',
        detail: errorMessage,
        life: 4000,
      })
      return
    }

    await noteStore.updateNoteFromStore(editingNote.value, {
      title: editNoteData.value.title.trim(),
      content: editNoteData.value.content,
    })
    editingNote.value = null

    // Restore scroll position after DOM update
    await nextTick()
    window.scrollTo(0, scrollPosition.value)
  }
}

const cancelEdit = () => {
  editingNote.value = null
  editNoteData.value = {
    title: '',
    content: '',
  }
  editTitleError.value = false
  editContentError.value = false

  // Restore scroll position after DOM update
  nextTick(() => {
    window.scrollTo(0, scrollPosition.value)
  })
}

// Clear title error when user starts typing
const onEditTitleInput = () => {
  if (
    editTitleError.value &&
    editNoteData.value.title &&
    editNoteData.value.title.trim().length > 0
  ) {
    editTitleError.value = false
  }
}

// Clear content error when user starts typing
const onEditContentChange = () => {
  if (editContentError.value && !isContentEmpty(editNoteData.value.content)) {
    editContentError.value = false
  }
}

// Watch for title changes to validate in real-time
watch(
  () => editNoteData.value.title,
  (newTitle) => {
    if (editingNote.value && (!newTitle || newTitle.trim().length === 0)) {
      editTitleError.value = true
    } else if (editingNote.value && newTitle && newTitle.trim().length > 0) {
      editTitleError.value = false
    }
  },
)

// Watch for content changes to validate in real-time
watch(
  () => editNoteData.value.content,
  (newContent) => {
    if (editingNote.value && isContentEmpty(newContent)) {
      editContentError.value = true
    } else if (editingNote.value && !isContentEmpty(newContent)) {
      editContentError.value = false
    }
  },
)
</script>

<template>
  <div class="note-list">
    <Toast />

    <div class="header">
      <div class="title-section">
        <i class="pi pi-file-edit title-icon"></i>
        <h2>Mes Notes</h2>
        <Badge
          v-if="hasNotes && IS_DEBUG"
          :value="noteStore.notesCount"
          severity="info"
          class="notes-badge"
        />
      </div>

      <div class="actions">
        <Button
          @click="fetchNotes"
          :loading="isLoading || refreshing"
          icon="pi pi-refresh"
          label="Actualiser"
          size="medium"
          severity="success"
          outlined
        />
      </div>
    </div>

    <!-- Notes Grid -->
    <div class="notes-grid">
      <!-- Empty state when no notes -->
      <Card v-if="!hasNotes && !isLoading" class="empty-state-card">
        <template #content>
          <div class="empty-state">
            <i class="pi pi-file-edit empty-icon"></i>
            <h3>Aucune note</h3>
            <p>Commencez par enregistrer votre première note</p>
          </div>
        </template>
      </Card>

      <!-- Existing Notes -->
      <Card
        v-if="hasNotes"
        v-for="note in notes.sort(
          (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
        )"
        :key="note.id_note"
        class="note-card"
        :class="{ editing: editingNote === note.id_note }"
      >
        <template #header>
          <div class="note-header">
            <div class="note-title-section">
              <i class="pi pi-file-edit note-icon"></i>
              <h3 v-if="editingNote !== note.id_note">{{ note.title }}</h3>
              <InputText
                v-else
                v-model="editNoteData.title"
                class="edit-title-input"
                placeholder="Titre de la note"
                :invalid="editTitleError"
                @input="onEditTitleInput"
              />
            </div>
            <div class="note-actions">
              <!-- Edit Mode Actions -->
              <template v-if="editingNote === note.id_note">
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
                  @click="startEdit(note)"
                  icon="pi pi-pencil"
                  severity="info"
                  text
                  rounded
                  size="medium"
                  :title="'Modifier'"
                />
                <Button
                  @click="(event) => cloneNote(event, note)"
                  icon="pi pi-copy"
                  severity="warning"
                  text
                  rounded
                  size="medium"
                  :title="'Dupliquer'"
                />
                <Button
                  @click="(event) => deleteNote(event, note.id_note, note.title)"
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
          <div class="note-content">
            <!-- Content Preview/Editor -->
            <div class="content-section">
              <label class="field-label">
                <i class="pi pi-file-text"></i>
                Contenu:
              </label>

              <!-- Preview Mode -->
              <div v-if="editingNote !== note.id_note" class="content-preview">
                <div v-if="note.content" v-html="note.content" class="content-html"></div>
                <p v-else class="content-text empty">Aucun contenu</p>
                <div class="content-meta">
                  <Tag :value="`${note.content?.length || 0} caractères`" severity="secondary" />
                </div>
              </div>

              <!-- Edit Mode -->
              <Editor
                v-else
                v-model="editNoteData.content"
                editorStyle="height: 300px; font-size: 1rem"
                class="content-editor"
                :class="{ 'edit-content-error': editContentError }"
                @text-change="onEditContentChange"
              >
                <template v-slot:toolbar>
                  <span class="ql-formats">
                    <button class="ql-header" value="1"></button>
                    <button class="ql-header" value="2"></button>
                  </span>
                  <span class="ql-formats">
                    <button class="ql-list" value="bullet"></button>
                  </span>
                </template>
              </Editor>
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
                    <Tag :value="note.id_note" severity="secondary" />
                  </div>

                  <div class="meta-item">
                    <span class="meta-label">
                      <i class="pi pi-calendar-plus"></i>
                      Créé:
                    </span>
                    <span class="meta-value">{{ formatDate(note.created_at) }}</span>
                  </div>

                  <div v-if="note.updated_at !== note.created_at" class="meta-item">
                    <span class="meta-label">
                      <i class="pi pi-calendar-times"></i>
                      Modifié:
                    </span>
                    <span class="meta-value">{{ formatDate(note.updated_at) }}</span>
                  </div>
                </div>
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
.note-list {
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

.notes-badge {
  margin-left: 0.5rem;
}

.error-message {
  margin-bottom: 1rem;
}

.empty-state-card {
  margin: 2rem 0;
  width: 100%;
  grid-column: 1 / -1;
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
  margin: 0;
  color: var(--text-color-secondary);
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1rem;
}

/* When there are no notes, make the empty state card take full width */
.notes-grid:has(.empty-state-card) {
  grid-template-columns: 1fr;
}

.note-card {
  background-color: var(--eerie-black-color);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.note-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: var(--surface-50);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
}

.note-title-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.note-icon {
  font-size: 1.25rem;
  color: var(--primary-color);
}

.note-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.25rem;
  font-weight: 600;
}

.note-content {
  padding: 1rem;
}

.content-section {
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

.content-preview {
  margin-top: 0.5rem;
}

.content-html {
  margin-bottom: 1rem;
  color: var(--text-color-secondary);
  line-height: 1.6;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--surface-border);
  padding: 1rem;
  border-radius: var(--border-radius);
  background: var(--surface-ground);
}

.content-text {
  margin: 0;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.content-text.empty {
  color: var(--text-color-secondary);
  font-style: italic;
}

.content-meta {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.content-editor {
  margin-top: 0.5rem;
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

.content-editor.edit-content-error :deep(.ql-editor) {
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 1px #ef4444 !important;
}

.content-editor.edit-content-error :deep(.ql-toolbar) {
  border-color: #ef4444 !important;
}

.content-editor.edit-content-error :deep(.ql-container) {
  border-color: #ef4444 !important;
}

.note-actions {
  display: flex;
  gap: 0.25rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .notes-grid {
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

  .note-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .note-actions {
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
  .note-header {
    background: var(--surface-100);
  }
}
</style>
