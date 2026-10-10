#!/usr/bin/env bash
set -euo pipefail

API_URL="${FRAUDMESH_API_URL:-http://127.0.0.1:8000}"
TOKEN="${FRAUDMESH_TOKEN:?Set FRAUDMESH_TOKEN to an application bearer token}"
AUTH=(-H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json")

echo "Ask the graph"
curl --fail-with-body -sS "${AUTH[@]}" -X POST "${API_URL}/api/network/ask" \
  --data '{"question":"Show accounts with alert score above 80"}'
echo

echo "Council of 3"
curl --fail-with-body -sS "${AUTH[@]}" -X POST "${API_URL}/api/alerts/ALERT-ACC-M3/council"
echo

echo "Scam script classifier"
curl --fail-with-body -sS "${AUTH[@]}" -X POST "${API_URL}/api/scam/classify" \
  --data '{"transcript":"Synthetic reminder: review your monthly statement through the official banking app."}'
echo
