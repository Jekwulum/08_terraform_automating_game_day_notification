provider "azurerm" {
  features {}

  client_id       = var.client_id
  client_secret   = var.client_secret
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# Resource group
# resource "azurerm_resource_group" "devops_rg" {
#   name     = var.resource_group_name
#   location = var.location
# }

# because the reource group is already created, we will use data block to get the resource group
data "azurerm_resource_group" "devops_rg" {
  name = var.resource_group_name
}

output "id" {
  value = data.azurerm_resource_group.devops_rg.id
}

# Storage account
resource "azurerm_storage_account" "function_app_storage" {
  name                     = "gamedaystorage"
  resource_group_name      = data.azurerm_resource_group.devops_rg.name
  location                 = data.azurerm_resource_group.devops_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Application Insights
resource "azurerm_application_insights" "function_app_insights" {
  name                = "gamedayappinsights"
  resource_group_name = data.azurerm_resource_group.devops_rg.name
  location            = data.azurerm_resource_group.devops_rg.location
  application_type    = "web"
}

# Service plan and function app
resource "azurerm_service_plan" "function_app_service_plan" {
  name                = "gamedayserviceplan"
  resource_group_name = data.azurerm_resource_group.devops_rg.name
  location            = data.azurerm_resource_group.devops_rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_function_app" "function_app" {
  name                = "gamedayfunctionapp"
  resource_group_name = data.azurerm_resource_group.devops_rg.name
  location            = data.azurerm_resource_group.devops_rg.location

  storage_account_name       = azurerm_storage_account.function_app_storage.name
  storage_account_access_key = azurerm_storage_account.function_app_storage.primary_access_key
  service_plan_id            = azurerm_service_plan.function_app_service_plan.id

  site_config {
    application_insights_key = azurerm_application_insights.function_app_insights.instrumentation_key

    application_stack {
      python_version = "3.11"
    }
  }

  identity {
    type = "SystemAssigned"
  }
}

# Event Grid Topic
resource "azurerm_eventgrid_topic" "function_app_event_grid_topic" {
  name                = "gamedayeventgridtopic"
  resource_group_name = data.azurerm_resource_group.devops_rg.name
  location            = data.azurerm_resource_group.devops_rg.location
}

# Logic App
resource "azurerm_logic_app_workflow" "function_app_logic_app" {
  name                = "gamedaylogicapp"
  resource_group_name = data.azurerm_resource_group.devops_rg.name
  location            = data.azurerm_resource_group.devops_rg.location
}

# Event Grid Subscription
resource "azurerm_eventgrid_event_subscription" "function_app_event_grid_subscription" {
  name  = "game-day-event-grid-subscription"
  scope = azurerm_eventgrid_topic.function_app_event_grid_topic.id

  webhook_endpoint {
    url = azurerm_logic_app_workflow.function_app_logic_app.access_endpoint
  }

  included_event_types = ["Microsoft.EventGrid.SubscriptionValidationEvent", "Microsoft.EventGrid.Event"]
}

# # Role assignments
# resource "azurerm_role_assignment" "function_to_eventgrid" {
#   scope                = azurerm_eventgrid_topic.function_app_event_grid_topic.id
#   role_definition_name = "EventGrid Data Sender"
#   principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id
# }

# resource "azurerm_role_assignment" "function_to_storage" {
#   scope                = azurerm_storage_account.function_app_storage.id
#   role_definition_name = "Storage Blob Data Contributor"
#   principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id
# }