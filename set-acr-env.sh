#!/bin/bash
# Source this script to set the ACR_ENDPOINT environment variable:
#   source ./set-acr-env.sh

if [ -z "${1:-}" ]; then
  echo "Usage: source ./set-acr-env.sh <your-acr-name-or-fqdn>"
  echo "Example: source ./set-acr-env.sh myacr.azurecr.io"
  return 1 2>/dev/null || exit 1
fi

ACR_ENDPOINT="$1"

# Append .azurecr.io if the user only provided the registry name
if [[ "$ACR_ENDPOINT" != *.azurecr.io ]]; then
  ACR_ENDPOINT="${ACR_ENDPOINT}.azurecr.io"
fi

export ACR_ENDPOINT
echo "ACR_ENDPOINT set to: ${ACR_ENDPOINT}"
