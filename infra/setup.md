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

## 6. Upload POS CSV files to Bronze layer

# Load credentials
source .env

# Upload 7 days of POS data
for date in 2026-05-23 2026-05-24 2026-05-25 2026-05-26 2026-05-27 2026-05-28 2026-05-29; do
  az storage fs file upload \
    --account-name retailpulsedatalake \
    --file-system bronze \
    --path pos/${date}/pos_transactions_${date}.csv \
    --source data-sources/pos-simulator/output/${date}/pos_transactions_${date}.csv \
    --account-key $ADLS_ACCOUNT_KEY
done

## 7. Create Databricks Workspace

az databricks workspace create \
  --name dbw-retailpulse-dev \
  --resource-group rg-retailpulse-dev \
  --location northeurope \
  --sku trial
