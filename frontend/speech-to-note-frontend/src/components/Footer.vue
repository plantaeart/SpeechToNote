<script setup lang="ts">
import { ref, computed } from 'vue'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import { VERSION } from '@/config/env.current'

const currentYear = computed(() => new Date().getFullYear())
const version = ref(VERSION)

const openLink = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}
</script>

<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-section">
        <div class="footer-brand">
          <i class="pi pi-microphone brand-icon"></i>
          <h3>SpeechToNote</h3>
        </div>
        <p class="footer-description">
          Application de gestion de commandes vocales et de notes intelligentes.
        </p>
      </div>
    </div>

    <Divider />

    <div class="footer-bottom">
      <div class="footer-copyright">
        <span>&copy; {{ currentYear }} SpeechToNote. Tous droits réservés.</span>
      </div>
      <div class="footer-version">
        <span>Version {{ version }}</span>
      </div>
      <div class="footer-tech">
        <span class="tech-stack">
          <i class="pi pi-code"></i>
          Vue.js • FastAPI • MongoDB
        </span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: var(--surface-card);
  border-top: 1px solid var(--surface-border);
  margin-top: auto;
  padding: 2rem 1rem 1rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.footer-section h3,
.footer-section h4 {
  margin: 0 0 1rem;
  color: var(--text-color);
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.brand-icon {
  font-size: 2rem;
  color: var(--primary-color);
}

.footer-brand h3 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-color);
}

.footer-description {
  margin: 0;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-link {
  padding: 0.25rem 0;
  color: var(--text-color-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--primary-color);
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.info-item i {
  font-size: 0.875rem;
  color: var(--primary-color);
  width: 1rem;
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-copyright,
.footer-tech {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.tech-stack {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tech-stack i {
  color: var(--primary-color);
}

/* Responsive Design */
@media (max-width: 768px) {
  .app-footer {
    padding: 1.5rem 1rem 1rem;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
}

/* Dark theme adjustments */
@media (prefers-color-scheme: dark) {
  .app-footer {
    background: var(--surface-ground);
  }
}
</style>
