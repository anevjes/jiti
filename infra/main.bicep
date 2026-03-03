@description('The location for the resources.')
param location string = resourceGroup().location

@description('The name of the Container Apps Environment.')
param environmentName string = 'env-${uniqueString(resourceGroup().id)}'

@description('The name of the Session Pool.')
param sessionPoolName string = 'session-pool-${uniqueString(resourceGroup().id)}'

@description('The name of the Container App for the MCP server.')
param appName string = 'jiti-mcp-server'

@description('The container image for the MCP server.')
param appImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest' // Placeholder, user to update

@description('Azure OpenAI Endpoint')
param azureOpenAiEndpoint string

@description('Azure OpenAI API Key')
@secure()
param azureOpenAiApiKey string

@description('Azure OpenAI Deployment Name')
param azureOpenAiDeploymentName string = 'gpt-4o'

@description('Azure OpenAI API Version')
param azureOpenAiApiVersion string = '2024-02-15-preview'

// Azure Container Apps Environment
resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  properties: {
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

// Dynamic Session Pool
resource sessionPool 'Microsoft.App/sessionPools@2024-02-02-preview' = {
  name: sessionPoolName
  location: location
  properties: {
    environmentId: managedEnvironment.id
    containerType: 'PythonLTS'
    poolManagementType: 'Dynamic'
    scaleConfiguration: {
      maxConcurrentSessions: 10
      readySessionInstances: 1
    }
    dynamicPoolConfiguration: {
      executionType: 'Timed'
      cooldownPeriodInSeconds: 300
    }
  }
}

// MCP Server Container App
resource mcpServer 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: managedEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8001
        transport: 'auto'
      }
      secrets: [
        {
          name: 'azure-openai-api-key'
          value: azureOpenAiApiKey
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'mcp-server'
          image: appImage
          resources: {
            cpu: 0.5
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: azureOpenAiEndpoint
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              secretRef: 'azure-openai-api-key'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: azureOpenAiDeploymentName
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: azureOpenAiApiVersion
            }
            {
              name: 'ACA_POOL_MANAGEMENT_ENDPOINT'
              value: sessionPool.properties.poolManagementEndpoint
            }
          ]
        }
      ]
    }
  }
}

// Role Assignment: Grant MCP Server permissions to execute code in Session Pool
// "Azure ContainerApps Session Executor" Role Definition ID: 0fb8eba5-a2bb-4abe-b1c1-49dfd8f52291
resource sessionExecutorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(sessionPool.id, mcpServer.id, 'AzureContainerAppsSessionExecutor')
  scope: sessionPool
  properties: {
    principalId: mcpServer.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0fb8eba5-a2bb-4abe-b1c1-49dfd8f52291')
    principalType: 'ServicePrincipal'
  }
}

output mcpServerUrl string = mcpServer.properties.configuration.ingress.fqdn
output sessionPoolId string = sessionPool.id
output sessionPoolManagementEndpoint string = sessionPool.properties.poolManagementEndpoint
