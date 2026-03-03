# Deploy the JITi Infrastructure

param (
    [string]$ResourceGroupName = "rg-jiti-mcp",
    [string]$Location = "eastus",
    [string]$AppImage = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest" # Default placeholder
)

# Load environment variables from .env file if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..."
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^(AZURE_OPENAI_[^=]+)=(.*)$") {
            # Trim quotes if present
            $key = $matches[1]
            $value = $matches[2] -replace '^"|"$', '' -replace "^'|'$", ''
            Set-Variable -Name $key -Value $value -Scope Script
        }
    }
}

# Check for required Azure OpenAI variables
if (-not $script:AZURE_OPENAI_ENDPOINT -or -not $script:AZURE_OPENAI_API_KEY) {
    Write-Error "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set in .env file or environment."
    exit 1
}

# Check Azure Login
Write-Host "Checking Azure login status..."
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "Logged in to subscription: $($account.name) ($($account.id))"
}
catch {
    Write-Error "Not logged in to Azure. Please run 'az login' first."
    exit 1
}

# Create Resource Group
Write-Host "Creating/Updating Resource Group '$ResourceGroupName' in '$Location'..."
az group create --name $ResourceGroupName --location $Location --output none

# Deploy Bicep
Write-Host "Deploying Infrastructure..."
$deployment = az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file infra/main.bicep `
    --parameters appImage=$AppImage `
                 azureOpenAiEndpoint=$script:AZURE_OPENAI_ENDPOINT `
                 azureOpenAiApiKey=$script:AZURE_OPENAI_API_KEY `
    --output json | ConvertFrom-Json

if ($deployment.properties.provisioningState -eq "Succeeded") {
    Write-Host "Deployment Succeeded!"
    Write-Host "--------------------------------------------------"
    Write-Host "MCP Server URL: $($deployment.properties.outputs.mcpServerUrl.value)"
    Write-Host "Session Pool ID: $($deployment.properties.outputs.sessionPoolId.value)"
    Write-Host "--------------------------------------------------"
}
else {
    Write-Error "Deployment failed."
}
