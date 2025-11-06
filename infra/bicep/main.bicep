// Main Bicep template for Azure resources
// Deploy: az deployment group create -g <rg> -f main.bicep -p environment=dev

@description('Environment name')
@allowed(['dev', 'stg', 'prd'])
param environment string = 'dev'

@description('Azure region')
param location string = resourceGroup().location

@description('Application name')
param appName string = 'agent-framework'

@description('Tags for resources')
param tags object = {
  Environment: environment
  Application: appName
  ManagedBy: 'Bicep'
}

// Variables
var uniqueSuffix = uniqueString(resourceGroup().id)
var storageAccountName = '${appName}${environment}${uniqueSuffix}'
var serviceBusNamespaceName = '${appName}-sb-${environment}'
var aiSearchName = '${appName}-search-${environment}'
var keyVaultName = '${appName}-kv-${environment}'
var appInsightsName = '${appName}-ai-${environment}'
var logAnalyticsName = '${appName}-la-${environment}'

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    encryption: {
      services: {
        blob: {
          enabled: true
        }
        file: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
  }
}

// Blob containers
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource checkpointsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'checkpoints'
  properties: {
    publicAccess: 'None'
  }
}

resource resultsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'results'
  properties: {
    publicAccess: 'None'
  }
}

// Service Bus Namespace
resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: serviceBusNamespaceName
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
}

// Service Bus Queue
resource jobQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'agent-jobs'
  properties: {
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    requiresSession: false
    deadLetteringOnMessageExpiration: true
    maxDeliveryCount: 10
  }
}

// Azure AI Search
resource aiSearch 'Microsoft.Search/searchServices@2023-11-01' = {
  name: aiSearchName
  location: location
  tags: tags
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
}

// Outputs
output storageAccountName string = storageAccount.name
output storageAccountConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
output serviceBusConnectionString string = listKeys(resourceId('Microsoft.ServiceBus/namespaces/authorizationRules', serviceBusNamespaceName, 'RootManageSharedAccessKey'), serviceBusNamespace.apiVersion).primaryConnectionString
output aiSearchEndpoint string = 'https://${aiSearch.name}.search.windows.net'
output aiSearchApiKey string = aiSearch.listAdminKeys().primaryKey
output keyVaultUri string = keyVault.properties.vaultUri
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
