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
