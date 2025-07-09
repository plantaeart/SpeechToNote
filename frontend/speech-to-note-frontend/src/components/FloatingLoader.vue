<script setup lang="ts">
import ProgressSpinner from 'primevue/progressspinner'

interface Props {
  visible?: boolean
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center'
  size?: 'small' | 'medium' | 'large'
  message?: string
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  position: 'bottom-right',
  size: 'small',
  message: '',
})

const getPositionClass = () => {
  switch (props.position) {
    case 'bottom-left':
      return 'bottom-left'
    case 'top-right':
      return 'top-right'
    case 'top-left':
      return 'top-left'
    case 'center':
      return 'center'
    default:
      return 'bottom-right'
  }
}

const getSizeClass = () => {
  switch (props.size) {
    case 'medium':
      return 'size-medium'
    case 'large':
      return 'size-large'
    default:
      return 'size-small'
  }
}
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" class="floating-loader" :class="[getPositionClass(), getSizeClass()]">
      <ProgressSpinner :size="size" />
      <span v-if="message" class="loader-message">{{ message }}</span>
    </div>
  </Transition>
</template>

<style scoped>
.floating-loader {
  position: fixed;
  background: var(--surface-card);
  border-radius: 0.75rem;
  padding: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  border: 2px solid var(--surface-border);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Position classes */
.bottom-right {
  bottom: 2rem;
  right: 2rem;
}

.bottom-left {
  bottom: 2rem;
  left: 2rem;
}

.top-right {
  top: 2rem;
  right: 2rem;
}

.top-left {
  top: 2rem;
  left: 2rem;
}

.center {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Size classes */
.size-small {
  padding: 0.75rem;
}

.size-small:deep(.p-progress-spinner) {
  width: 2rem;
  height: 2rem;
}

.size-medium {
  padding: 1rem;
}

.size-medium:deep(.p-progress-spinner) {
  width: 2.5rem;
  height: 2.5rem;
}

.size-large {
  padding: 1.25rem;
}

.size-large:deep(.p-progress-spinner) {
  width: 3rem;
  height: 3rem;
}

.loader-message {
  font-size: 0.875rem;
  color: var(--text-color);
  font-weight: 500;
  white-space: nowrap;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
