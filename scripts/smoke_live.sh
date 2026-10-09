#!/usr/bin/env bash
set -euo pipefail

: "${NEMOTRON_BASE_URL:?Set NEMOTRON_BASE_URL}"
: "${NEMOTRON_API_KEY:?Set NEMOTRON_API_KEY}"
: "${NEMOTRON_MODEL:?Set NEMOTRON_MODEL}"

python -m app.cli nemotron-smoke --prompt 'Reply with the single word READY.'
