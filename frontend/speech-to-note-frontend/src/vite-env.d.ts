/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CONFIG_ENV_FRONT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
