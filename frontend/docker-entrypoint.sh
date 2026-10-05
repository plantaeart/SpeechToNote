#!/bin/sh
# Generates /usr/share/nginx/html/env.js from environment variables at container
# start, so the Google Cloud API key is never baked into an image layer.
set -eu

OUTPUT="/usr/share/nginx/html/env.js"

if [ -z "${GCP_API_KEY:-}" ]; then
  echo "⚠️  GCP_API_KEY is not set — speech recognition will not work."
  echo "   Set it in infra/.env (see the README)."
fi

# Escape backslashes and quotes so a value can never break out of the string.
escape() {
  printf '%s' "${1:-}" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

GCP_KEY_ESCAPED=$(escape "${GCP_API_KEY:-}")
API_URL_ESCAPED=$(escape "${API_BASE_URL:-http://localhost:8000}")

cat > "$OUTPUT" <<EOF
// Generated at container start by docker-entrypoint.sh — do not edit.
window.__SPEECHTONOTE_ENV__ = {
  GCP_API_KEY: "${GCP_KEY_ESCAPED}",
  API_BASE_URL: "${API_URL_ESCAPED}"
};
EOF

echo "✅ Wrote $OUTPUT"

exec nginx -g 'daemon off;'