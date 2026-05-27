# Architecture Decision Records

## ADR-001: Repository Structure
**Date:** 2026-05-28
**Status:** Accepted

**Context:**
Starting a new data engineering project (RetailPulse) from scratch. 
Need a folder production grade folder structure

**Decision:**
Separate top-level folders by concern: infra, data-sources, databricks, 
powerbi, docs. CI/CD lives in .github/workflows.

**Consequences:**
- Clear separation between infrastructure code, transformation logic, 
  and source simulators
- Any new contributor can navigate the repo without explanation

---

## ADR-002: CLI-First Infrastructure Provisioning
**Date:** 2026-05-28  
**Status:** Accepted

**Context:**
Azure resources can be provisioned via Portal UI or Azure CLI.

**Decision:**
All provisioning done via Azure CLI. Commands documented in infra/setup.md. 
Portal used only for verification and visual inspection.

**Consequences:**
- Every infrastructure decision is reproducible and version-controlled
- infra/setup.md becomes a runbook anyone can follow
- Demonstrating infrastructure-as-code thinking to employers
