# Source this script to set the ACR_ENDPOINT environment variable:
#   . .\set-acr-env.ps1 <your-acr-name-or-fqdn>

param(
  [Parameter(Mandatory = $false, Position = 0)]
  [string]$AcrName
)

if (-not $AcrName) {
  Write-Host "Usage: . .\set-acr-env.ps1 <your-acr-name-or-fqdn>"
  Write-Host "Example: . .\set-acr-env.ps1 myacr.azurecr.io"
  return
}

# Append .azurecr.io if the user only provided the registry name
if ($AcrName -notlike "*.azurecr.io") {
  $AcrName = "$AcrName.azurecr.io"
}

$env:ACR_ENDPOINT = $AcrName
Write-Host "ACR_ENDPOINT set to: $env:ACR_ENDPOINT"
