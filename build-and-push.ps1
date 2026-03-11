#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

# Image name and tag
$ImageName = "jiti-mcp-server"
$ImageTag = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "latest" }

# Validate ACR_ENDPOINT is set
if (-not $env:ACR_ENDPOINT) {
  Write-Error "ACR_ENDPOINT environment variable is not set.`nUsage: `$env:ACR_ENDPOINT = '<your-acr>.azurecr.io'; .\build-and-push.ps1"
  exit 1
}

# Strip any trailing slash
$AcrEndpoint = $env:ACR_ENDPOINT.TrimEnd('/')

$FullImage = "${AcrEndpoint}/${ImageName}:${ImageTag}"

Write-Host "==> Authenticating to ACR: $AcrEndpoint using logged-in Azure credentials..."
az acr login --name $AcrEndpoint
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Building Docker image: $FullImage..."
docker build -t $FullImage .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Pushing image to ACR: $FullImage..."
docker push $FullImage
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Done. Image pushed: $FullImage"
