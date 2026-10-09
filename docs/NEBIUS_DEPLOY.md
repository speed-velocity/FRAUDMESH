# Nebius deployment

FraudMesh uses Nebius Token Factory for optional live Nemotron reasoning and can run its FastAPI backend as a container on Nebius AI Cloud.

## Verified Token Factory configuration

Nebius documents an OpenAI-compatible endpoint at `https://api.tokenfactory.nebius.com/v1/` with `POST /v1/chat/completions`. The backend keeps the existing `NEMOTRON_*` names so Render, local Docker, and Nebius use the same configuration:

```bash
export NEMOTRON_BASE_URL=https://api.tokenfactory.nebius.com/v1
export NEMOTRON_API_KEY='replace-with-your-token-factory-key'
export NEMOTRON_MODEL='nvidia/nemotron-3.5-lightning-30b-a3b'
```

Model IDs are account/catalog dependent. Verify the exact Nemotron ID in the Token Factory model catalog before setting `NEMOTRON_MODEL`; do not put the key in the frontend or repository.

## Build and run the backend container

From the repository root:

```bash
docker build -f backend/Dockerfile -t fraudmesh-api:local .
docker run --rm -p 8000:8000 \
  -e APP_ENV=demo \
  -e JWT_SECRET="$(openssl rand -hex 32)" \
  -e DEMO_INVESTIGATOR_PASSWORD='replace-with-12-character-password' \
  -e DEMO_ADMIN_PASSWORD='replace-with-12-character-password' \
  -e NEMOTRON_BASE_URL='https://api.tokenfactory.nebius.com/v1' \
  -e NEMOTRON_API_KEY='replace-with-your-token-factory-key' \
  -e NEMOTRON_MODEL='nvidia/nemotron-3.5-lightning-30b-a3b' \
  fraudmesh-api:local
curl http://127.0.0.1:8000/api/v1/health
```

## Nebius AI Cloud

1. Create or select a Nebius AI Cloud project and an authenticated CLI profile.
2. Push this image to a registry accessible by that project, or build it on a Compute VM.
3. Run the container with the environment variables above, using a persistent volume for `data/runtime` if demo state must survive restarts.
4. Expose TCP port `8000` through the project network and point `VITE_API_ORIGIN` at the resulting HTTPS URL.
5. Verify `/api/v1/health`, login, and the Live Alerts → Explain with Nemotron flow.

The exact Nebius AI Cloud container/serverless product and CLI flags vary by account and region. **TODO (account-specific):** replace the generic container steps with the selected Nebius Serverless Endpoint or Compute VM command after that service is enabled in the target project. Do not infer endpoint flags from this document.

## Frontend configuration

Set `VITE_API_ORIGIN` at frontend build time:

```bash
VITE_API_ORIGIN=https://your-nebius-backend.example npm run build
```

The frontend uses the existing API-origin normalization layer; no API key is shipped to the browser.
