// Default runtime configuration.
//
// In Docker, frontend/docker-entrypoint.sh overwrites this file at container
// start from the GCP_API_KEY environment variable, so the key is never baked
// into an image layer. When running `npm run dev`, this file is used as-is.
window.__SPEECHTONOTE_ENV__ = {
  GCP_API_KEY: '',
  API_BASE_URL: '',
};