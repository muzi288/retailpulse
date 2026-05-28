# RetailPulse — Infrastructure Setup

This runbook documents every Azure resource provisioned for RetailPulse.
All commands use Azure CLI. Run them in order.

## Prerequisites
- Azure CLI installed (`az --version`)
- Active Azure subscription
- Logged in (`az login`)

---

## 1. Verify Subscription

```bash
az account show --output table
## 2. Create Resource Group

az group create \
  --name rg-retailpulse-dev \
  --location southafricanorth

## 3. Create ADLS Gen2 Storage Account

az storage account create \
  --name retailpulsedatalake \
  --resource-group rg-retailpulse-dev \
  --location southafricanorth \
  --sku Standard_LRS \
  --kind StorageV2 \
  --hierarchical-namespace true

## 4. Create Bronze/Silver/Gold Containers

az storage fs create -n bronze --account-name retailpulsedatalake
az storage fs create -n silver --account-name retailpulsedatalake
az storage fs create -n gold --account-name retailpulsedatalake

## 5. Create Azure Data Factory

az datafactory create \
  --name adf-retailpulse-muzi \
  --resource-group rg-retailpulse-dev \
  --location southafricanorth
