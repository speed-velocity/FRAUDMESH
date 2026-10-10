#!/usr/bin/env bash
set -euo pipefail

: "${FRAUDMESH_API_URL:=http://127.0.0.1:8000}"
: "${FRAUDMESH_TOKEN:?Set FRAUDMESH_TOKEN to an application bearer token first}"

curl --fail-with-body --silent --show-error \
  -X POST "${FRAUDMESH_API_URL%/}/api/chat" \
  -H "Authorization: Bearer ${FRAUDMESH_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"message":"Why did ACC-M3 surface?","conversation_id":"smoke-nemo","page_context":{"entity_id":"ACC-M3"}}'
printf '\n'
