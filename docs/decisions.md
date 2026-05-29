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

## ADR-003: Simplified POS Transaction Schema
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
In a real retail POS system, a single transaction is a basket containing 
multiple line items — one receipt can have rice, cooking oil, and bread 
as separate line items under one transaction_id.

**Decision:**
For the simulator, each transaction contains one product (one line item). 
This simplifies data generation while still demonstrating the full 
Bronze → Silver → Gold pipeline.

**Consequences:**
- Easier to generate and reason about in the simulator
- Does not reflect real POS schema complexity
- In production, schema would require both transaction_id (basket) and 
  line_item_id (individual product), identical pattern to e-commerce orders
- Silver layer deduplication logic would need to operate at line_item level,
  not transaction level

---

## ADR-004: Simplified E-commerce Order Schema  
**Date:** 2026-05-29
**Status:** Accepted

**Context:**
Real e-commerce orders contain a basket of items under one order_id,
each with its own line_item_id.

**Decision:**
Simulator generates one product per order for consistency with POS 
simulator and pipeline simplicity.

**Consequences:**
- Same tradeoffs as ADR-003
- In production, aggregations at Gold layer would need to GROUP BY 
  order_id before summing revenue to avoid double-counting

