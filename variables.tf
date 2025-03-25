variable "client_id" {
  description = "The Client ID (App ID) of the service principal"
  type        = string
}

variable "client_secret" {
  description = "The client secret of the service principal"
  type        = string
  sensitive   = true
}

variable "subscription_id" {
  description = "The Subscription ID of the service principal"
  type        = string
}

variable "tenant_id" {
  description = "The Tenant ID of the service principal"
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
  default     = "rg-devopschallenge"
}

variable "location" {
  description = "The location of the resource group"
  type        = string
  default     = "eastus2"
}