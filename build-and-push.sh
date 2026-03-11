#!/bin/bash
set -euo pipefail

# Image name and tag
IMAGE_NAME="jiti-mcp-server"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Validate ACR_ENDPOINT is set
if [ -z "${ACR_ENDPOINT:-}" ]; then
  echo "ERROR: ACR_ENDPOINT environment variable is not set."
  echo "Usage: ACR_ENDPOINT=<your-acr>.azurecr.io ./build-and-push.sh"
  exit 1
fi

# Strip any trailing slash
ACR_ENDPOINT="${ACR_ENDPOINT%/}"

FULL_IMAGE="${ACR_ENDPOINT}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "==> Authenticating to ACR: ${ACR_ENDPOINT} using logged-in Azure credentials..."
az acr login --name "${ACR_ENDPOINT}"

echo "==> Building Docker image: ${FULL_IMAGE}..."
docker build -t "${FULL_IMAGE}" .

echo "==> Pushing image to ACR: ${FULL_IMAGE}..."
docker push "${FULL_IMAGE}"

echo "==> Done. Image pushed: ${FULL_IMAGE}"
